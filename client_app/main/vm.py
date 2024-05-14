from PySide6.QtCore import QObject, Slot, Signal

from client_app.services.processing_mode_selector import ProcessingModeSelector
from common.services.face_scanning.face_scanner import FaceScannerService
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.project import AttentionProject
from common.services.video.types import VideoService



class ClientMainWindowVM(QObject):
    can_show_networking_page_changed = Signal(bool)
    can_show_offline_project_select_page_changed = Signal(bool)
    can_show_person_select_page_changed = Signal(bool)

    focus_networking_page = Signal()
    focus_offline_page = Signal()
    def __init__(self, 
                 processing_mode_selector:ProcessingModeSelector,
                 scene_initializer:AttentionSceneInitializerService,
                 video_service:VideoService,
                 face_scanner:FaceScannerService
                 ) -> None:
        super().__init__()
        self._processing_mode_selector = processing_mode_selector
        self._scene_initializer = scene_initializer
        self._video_service = video_service
        self._face_scanner = face_scanner
        self._old_project:AttentionProject|None = None
        self._scene_initializer.attention_project_changed.connect(self._attention_project_changed)
    @Slot(ProcessingModeSelector.RunningMode)
    def _observe_running_mode_changed(self, mode:ProcessingModeSelector.RunningMode):
        self.can_show_networking_page_changed.emit(self.can_show_networking_page())
        self.can_show_offline_project_select_page_changed.emit(self.can_show_offline_project_select_page())
        if mode == ProcessingModeSelector.RunningMode.Online:
            self.focus_networking_page.emit()
        else:
            self.focus_offline_page.emit()

    @Slot()
    def _attention_project_changed(self):
        project = self._scene_initializer.project()
        
        need_emit_change = False
        if project is None and self._old_project is not None or\
            project is not None and self._old_project is None:
            need_emit_change = True
        self._old_project = project

        if need_emit_change:
            self.can_show_person_select_page_changed.emit(self.can_show_person_select_page()) 


    def running_online(self):
        return self._processing_mode_selector.running_mode() == ProcessingModeSelector.RunningMode.Online

    def set_run_online(self):
        self._processing_mode_selector.set_online_mode()

    def set_run_offline(self):
        self._processing_mode_selector.set_offline_mode()

    def can_show_networking_page(self):
        return self._processing_mode_selector.running_mode() == ProcessingModeSelector.RunningMode.Online
    
    def can_show_offline_project_select_page(self):
        return self._processing_mode_selector.running_mode() == ProcessingModeSelector.RunningMode.Offline
    
    def can_show_person_select_page(self):
        return self._scene_initializer.project() is not None
    
    def close(self):
        
        self._video_service.stop()
        self._face_scanner.stop()