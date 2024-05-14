from aiohttp import web as aio_web
import socketio #type:ignore

from PySide6.QtCore import QObject, Signal, Slot
from common.domain.interfaces import AttentionScene, Person
from common.dtos.head_data import HeadData, HeadDataAdapter, PersonHeadDataAdapter
from common.dtos.hits import PerformedRayCastResultAdapter, PersonPerformedRayCastResultAdapter, SceneObjAggregatedHitsAdapter, SceneObjAttentionHitsAdapter
from common.dtos.states import AttentionSceneStateAdapter
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.utils import ProjectInfo
from web.apps.server.project_exporter import ActiveProjectExporter
from web.collections.connected_clients import ConnectedClientsCollection
from web.collections.exposed_persons import ExposedPersonsCollection
from web.domain.connected_client import ConnectedClient
import asyncio
from threading import Thread

from web.utils import ConnectionEventsNames, PersonIdData, PersonIdDataAdapter, find_free_port, get_ip



class ServerApp(QObject):
    running_changed = Signal(bool)

    project_prepare_started = Signal()
    project_prepare_ready = Signal()
    project_prepare_failed = Signal(str)

    def __init__(self, 
                 active_project_exporter:ActiveProjectExporter,
                 app:aio_web.Application,
                 io_server:socketio.AsyncServer,
                 scene_initializer:AttentionSceneInitializerService,
                 exposed_persons_collection:ExposedPersonsCollection,
                 connected_clients_collection:ConnectedClientsCollection
                 ) -> None:
        super().__init__()
        self._active_project_exporter = active_project_exporter
        self._app = app
        self._app.on_startup.append(self._observe_app_startup)
        self._app.on_shutdown.append(self._observe_app_shutdown)
        self._io_server = io_server
        self._io_server.attach(self._app)
        self._port = 0
        self._event_loop:asyncio.AbstractEventLoop|None = None
        self._scene_initializer = scene_initializer
        self._connected_clients = connected_clients_collection
        self._exposed_persons_collection = exposed_persons_collection

        self._scene_prepared = self.project_prepared()
        self._active_project_exporter.active_project_archive_started.connect(self._active_project_export_started)
        self._active_project_exporter.active_project_archive_failed.connect(self._active_project_export_failed)
        self._active_project_exporter.active_project_archive_complete.connect(self._active_project_export_complete)

        self._app.add_routes([aio_web.get(ConnectionEventsNames.active_project_download.value, self._send_active_project_archive)]) # type:ignore

        self._active_project_exporter.active_project_archive_changed.connect(self._active_project_archive_changed)
        self._io_server.on(ConnectionEventsNames.connect.value, self._handle_connect)
        self._io_server.on(ConnectionEventsNames.disconnect.value, self._handle_disconnect)
        self._io_server.on(ConnectionEventsNames.generated_head_data.value, self._handle_generated_head_data)
        self._io_server.on(ConnectionEventsNames.generated_scene_obj_aggregated_hits.value, self._handle_generated_aggregated_hits)
        self._io_server.on(ConnectionEventsNames.generated_cast_result.value, self._handle_generated_cast_result)
        self._io_server.on(ConnectionEventsNames.request_state.value, self._handle_request_state) #type:ignore

        self._app_running = False

    def run(self):
        if self.running():
            return
        self._server_thread = Thread(target=self._run_server_in_thread, daemon=True)
        self._server_thread.start()

    def _run_server_in_thread(self):
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        port = find_free_port()
        self._port = port
        aio_web.run_app(self._app, host='0.0.0.0', port=port, loop=self._get_server_event_loop())
    
    def _get_server_event_loop(self) -> asyncio.AbstractEventLoop:
        if self._event_loop is None:
            raise RuntimeError('ServerApp event loop is not initialized')
        return self._event_loop

    def stop(self):
        if self.running():
            asyncio.run_coroutine_threadsafe(self._shutdown(), self._get_server_event_loop())
            self._run_thread = None

    def running(self) -> bool:
        return self._app_running
    
    async def _observe_app_startup(self, app):
        self._app_running = True
        self.running_changed.emit(self._app_running)

    async def _observe_app_shutdown(self, app):
        self._app_running = False
        self.running_changed.emit(self._app_running)
    
    def project_prepared(self) -> bool:
        return self._active_project_exporter.active_project_archive() is not None

    @Slot(ProjectInfo)
    def _active_project_export_started(self, project_info:ProjectInfo):
        self.project_prepare_started.emit()

    @Slot(ProjectInfo, str)
    def _active_project_export_failed(self, project_info:ProjectInfo, reason:str):
        self.project_prepare_failed.emit(reason)
    
    @Slot(ProjectInfo)
    def _active_project_export_complete(self, project_info:ProjectInfo):
        self.project_prepare_ready.emit()

    async def _shutdown(self, ):
        await self._io_server.shutdown()
        await self._app.shutdown()
        await self._app.cleanup()
        self._port = 0

    def ip(self) -> str:
        return get_ip()
    
    def port(self) -> int:
        return self._port

    def _active_scene(self) -> AttentionScene|None:
        return pr.scene() if (pr:=self._scene_initializer.project()) is not None else None

    @Slot()
    def _active_project_archive_changed(self):
        # asyncio.run_coroutine_threadsafe(self._io_server.emit(ConnectionEventsNames.recieved_project_changed), self._get_server_event_loop())
        info = self._active_project_exporter.active_project_info()
        info_json = info.to_json() if info else ''
        asyncio.run_coroutine_threadsafe(self._io_server.emit(ConnectionEventsNames.recieved_project_changed, info_json), self._get_server_event_loop())

    def exposed_persons(self) -> ExposedPersonsCollection:
        return self._exposed_persons_collection

    async def _send_active_project_archive(self, request):
        archive_path = self._active_project_exporter.active_project_archive()
        if archive_path:
            return aio_web.FileResponse(archive_path)
        else:
            return aio_web.Response(status=404, text=f'No active project')
    
    @Slot()
    def _connected_client_person_changed(self):
        client = self.sender()
        if not isinstance(client, ConnectedClient):
            return
        person = client.person()

        person_id_data = PersonIdData(person_id=person.element_id() if person else None)
        asyncio.run_coroutine_threadsafe(self._io_server.emit(ConnectionEventsNames.recieved_current_person_id, 
                                            PersonIdDataAdapter.dump_json(person_id_data), 
                                            to=client.sid()), self._get_server_event_loop())

    async def _handle_connect(self):
        sid:str = request.sid # type:ignore
        connected_client = ConnectedClient(sid)
        connected_client.person_changed.connect(self._connected_client_person_changed)
        self._connected_clients.add_client(connected_client)

    # Handlers
    async def _handle_disconnect(self):
        sid:str = request.sid #type:ignore
        cl = self._connected_clients.get_by_sid(sid)
        if cl:
            cl.notify_connection_closed()

    async def _handle_generated_head_data(self, person_head_data_jsonb:bytes):
        person_head_data = PersonHeadDataAdapter.validate_json(person_head_data_jsonb)

        sid:str = request.sid # type:ignore
        cl = self._connected_clients.get_by_sid(sid)
        if cl and (person:=cl.person()) is not None:
            person.set_head_data(person_head_data.head_data)
            await self._io_server.emit(ConnectionEventsNames.recieved_others_head_data, person_head_data_jsonb, skip_sid=sid)

    async def _handle_generated_aggregated_hits(self, data:bytes):
        scene_obj_aggregated_hits = SceneObjAggregatedHitsAdapter.validate_json(data)

        sid:str = request.sid # type:ignore
        
        scene = self._active_scene()
        if scene:
            scene_obj = scene.scene_objs_by_id()[scene_obj_aggregated_hits.scene_obj_id]
            scene_obj.set_aggregated_hits(scene_obj_aggregated_hits.hits)
            await self._io_server.emit(ConnectionEventsNames.recieved_others_aggregated_hits.value, data, skip_sid=sid)

    async def _handle_generated_cast_result(self, cast_result_jsonb:bytes):
        cast_result = PersonPerformedRayCastResultAdapter.validate_json(cast_result_jsonb)

        sid:str = request.sid # type:ignore
        cl = self._connected_clients.get_by_sid(sid)
        if cl and (person:=cl.person()) is not None:
            person.set_performed_ray_cast_result(cast_result.cast_result)
            await self._io_server.emit(ConnectionEventsNames.recieved_others_cast_result.value, cast_result_jsonb, skip_sid=sid)

    async def _handle_request_state(self, _):
        sid:str = request.sid # type:ignore

        scene = self._active_scene()
        if scene:
            state_jsonb = AttentionSceneStateAdapter.dump_json(scene.export_state())
        else:
            state_jsonb = b''
        
        await self._io_server.emit(ConnectionEventsNames.recieved_state.value, state_jsonb, to=sid)
