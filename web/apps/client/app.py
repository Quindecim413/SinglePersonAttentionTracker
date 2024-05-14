from datetime import datetime
from pathlib import Path
from re import L
import tempfile
import threading
from uuid import uuid4
from PySide6.QtCore import QObject, Slot, Signal
import asyncio
from socketio import AsyncClient #type:ignore

from common.domain.interfaces import AttentionScene, Person
from common.dtos.head_data import PersonHeadDataAdapter
from common.dtos.hits import PersonPerformedRayCastResultAdapter, SceneObjAggregatedHitsAdapter
from common.dtos.states import AttentionSceneStateAdapter
from common.services.active_person import ActivePersonSelector
from common.services.scene.importers import ProjectFromLocalArchiveImporter
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.repo import AttentionProjectsRepo, ProjectImportProcess
from web.utils import ConnectionEventsNames, PersonIdDataAdapter, download_file


class ClientApp(QObject):
    # active_project_changed =Signal()
    active_project_fetch_started = Signal()
    active_project_fetch_complete = Signal()
    active_project_fetch_failed = Signal(str)
    active_project_import_complete = Signal()
    active_project_import_failed = Signal(str)
    active_project_sync_complete = Signal()
    active_project_sync_failed = Signal()

    connecting = Signal()
    connected = Signal()
    disconnected = Signal()
    connection_failed = Signal(str)

    enabled_changed = Signal(bool)

    def __init__(self, 
                 projects_archives_dir:Path,
                 client:AsyncClient,
                 person_selector:ActivePersonSelector,
                 projects_repo:AttentionProjectsRepo,
                 scene_initializer:AttentionSceneInitializerService,
                 ) -> None:
        super().__init__()
        self._projects_archives_dir = projects_archives_dir
        self._client = client
        self._person_selector = person_selector
        self._projects_repo = projects_repo
        self._scene_initializer = scene_initializer
        self._import_processes: list[ProjectImportProcess] = []
        
        self._old_active_person:Person|None = None
        self._person_selector.active_person_changed.connect(self._handle_selector_person_changed)
        self._event_loop:asyncio.AbstractEventLoop|None = None
        self._client_thread:threading.Thread|None = None
        self._client.on(ConnectionEventsNames.connect.value, self._handle_connected)
        self._client.on(ConnectionEventsNames.disconnect.value, self._handle_disconnected)
        self._client.on(ConnectionEventsNames.recieved_project_changed.value, self._handle_project_changed)
        self._client.on(ConnectionEventsNames.recieved_current_person_id.value, self._handle_recieved_current_person_id)
        self._client.on(ConnectionEventsNames.recieved_others_head_data.value, self._handle_recieved_others_head_data)
        self._client.on(ConnectionEventsNames.recieved_others_cast_result.value, self._handle_recieved_others_cast_result)
        self._client.on(ConnectionEventsNames.recieved_others_aggregated_hits.value, self._handle_recieved_others_aggregated_hits)
        self._client.on(ConnectionEventsNames.recieved_state.value, self._handle_recieved_state)
        self._enabled = True

    def _handle_enabled_changed(self, enabled:bool):
        if not enabled and self.is_connected():
            self.close_connection()
        
        for import_proc in self._import_processes:
            import_proc.cancel()

    def set_enabled(self, val:bool):
        val = bool(val)
        if val != self._enabled:
            self._enabled = val
            self.enabled_changed.emit(val)
            self._handle_enabled_changed(val)

    def is_enabled(self) -> bool:
        return self._enabled
    
    def is_connected(self) -> bool:
        return self._client.connected

    def _get_client_event_loop(self) -> asyncio.AbstractEventLoop:
        if self._event_loop is None:
            raise RuntimeError('ClientApp event loop is not initialized')
        return self._event_loop

    def connect(self, ip:str, port:int):
        if not self.is_enabled():
            return
        if self.is_connected():
            return
        if self._client_thread is not None:
            raise RuntimeError('_client_thread should be stopped before reconnecting')
        self._client_thread = threading.Thread(target=self._connect_in_thread, args=(ip, port), daemon=True)
        self._client_thread.start()

    def close_connection(self):
        if self._client.connected:
            asyncio.run_coroutine_threadsafe(self._client.disconnect(), self._get_client_event_loop())

    def _connect_in_thread(self, ip:str, port:int):
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_until_complete(self._connect_client(ip, port))

    async def _connect_client(self, ip:str, port:int):
        self._server_ip = ip
        self._server_port = port
        self._event_loop = asyncio.get_event_loop()
        try:
            self.connecting.emit()
            await self._client.connect(f'http://{self._server_ip}:{self._server_port}')
            self.connected.emit()
            await self._client.wait()
        except Exception as e:
            self.connection_failed.emit(str(e))
        finally:
            self.disconnected.emit()

    async def _handle_connected(self):
        # self.connected.emit()
        pass

    async def _handle_disconnected(self):
        self._client_thread = None
        # self.di

    def _request_update_state(self):
        asyncio.run_coroutine_threadsafe(self._client.emit(ConnectionEventsNames.request_state.value), self._get_client_event_loop())

    def _active_scene(self) -> AttentionScene|None:
        return pr.scene() if (pr:=self._scene_initializer.project()) is not None else None
    
    def _get_active_scene_strict(self):
        scene = self._active_scene()
        if scene is None:
            raise RuntimeError('active scene is not initialized yet')
        return scene

    # networking handlers
    async def _handle_project_changed(self, project_info_json:str):
        if not project_info_json:
            self._scene_initializer.set_project_data(None)
        else:
            # project_info = ProjectInfo.from_json(project_info_json)
            self._start_project_download()    

    async def _handle_recieved_current_person_id(self, data:bytes):
        person_id_data = PersonIdDataAdapter.validate_json(data)
        scene = self._get_active_scene_strict()
        
        person_id = person_id_data.person_id
        if person_id is not None:
            self._person_selector.set_active_person(scene.persons_by_id()[person_id])
        else:
            self._person_selector.set_active_person(None)
        
    async def _handle_recieved_others_head_data(self, data:bytes):
        person_head_data = PersonHeadDataAdapter.validate_json(data)
        active_person = self._person_selector.active_person()

        person_id = person_head_data.person_id
        
        if active_person and active_person.element_id() == person_id:
            return
        
        scene = self._get_active_scene_strict()
        scene.persons_by_id()[person_id].set_head_data(person_head_data.head_data)
        
    async def _handle_recieved_others_cast_result(self, data:bytes):
        cast_resuls = PersonPerformedRayCastResultAdapter.validate_json(data)
        person_id = cast_resuls.person_id

        scene = self._get_active_scene_strict()
        scene.persons_by_id()[person_id].set_performed_ray_cast_result(cast_resuls.cast_result)

    async def _handle_recieved_others_aggregated_hits(self, data:bytes):
        scene_obj_aggregated_hits = SceneObjAggregatedHitsAdapter.validate_json(data)

        scene_obj_id = scene_obj_aggregated_hits.scene_obj_id

        scene = self._get_active_scene_strict()
        scene.scene_objs_by_id()[scene_obj_id].set_aggregated_hits(scene_obj_aggregated_hits.hits)

    async def _handle_recieved_state(self, data:bytes):
        scene_state = AttentionSceneStateAdapter.validate_json(data)
        scene = self._get_active_scene_strict()
        scene.update_with_state(scene_state)

    # helper functions
        
    @Slot()
    def _handle_selector_person_changed(self):
        new_person = self._person_selector.active_person()
        if new_person != self._old_active_person:
            if self._old_active_person:
                self._old_active_person.disconnect(self)
            
            self._old_active_person = new_person


    def _start_project_download(self,):
        self._download_thread = threading.Thread(target=self._threaded_active_project_download)
        self._download_thread.start()

    def _threaded_active_project_download(self):
        try:
            self.active_project_fetch_started.emit()
            save_file = self._projects_archives_dir / f'{datetime.now().isoformat}.zip'
            download_file(f'http://{self._server_ip}:{self._server_port}/{ConnectionEventsNames.active_project_download}', 
                        save_file)
            self.active_project_fetch_complete.emit()
            project_import_process = self._projects_repo.create_import_project_process(ProjectFromLocalArchiveImporter(save_file))
            self._import_processes.append(project_import_process)
            self._bind_import_process_signals(project_import_process)
            
        except Exception as e:
            self.active_project_fetch_failed.emit(str(e))

    def _bind_import_process_signals(self, import_process:ProjectImportProcess):
        import_process.complete.connect(self._handle_import_complete)
        import_process.failed.connect(self._handle_import_failed)
        import_process.cancelled.connect(self._handle_import_cancelled)

    
    def _handle_import_complete(self):
        import_process = self.sender()
        if not isinstance(import_process, ProjectImportProcess):
            raise RuntimeError()
        self._import_processes.remove(import_process)
        self.active_project_import_complete.emit()
        self._request_update_state()

    def _handle_import_failed(self, reason:str):
        import_process = self.sender()
        if not isinstance(import_process, ProjectImportProcess):
            raise RuntimeError()
        self._import_processes.remove(import_process)
        self.active_project_import_failed.emit(reason)
    
    def _handle_import_cancelled(self):
        import_process = self.sender()
        if not isinstance(import_process, ProjectImportProcess):
            raise RuntimeError()
        self._import_processes.remove(import_process)
        self.active_project_import_failed.emit('Импорт отменён')

    
