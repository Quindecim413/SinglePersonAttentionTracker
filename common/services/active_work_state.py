import datetime
from PySide6.QtCore import QObject, Slot, Signal, QTimer
from client_app.services.processing_mode_selector import ProcessingModeSelector
from common.domain.interfaces import AttentionScene, Person
from common.services.active_person import ActivePersonSelector
from common.services.gaze.callibration import PersonGazeCallibrationService
from common.services.gaze.estimation import PersonGazeEstimationService
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.scene_3d import AttentionScene3DService
from web.apps.client.app import ClientApp


class ActiveWorkState(QObject):
    active_scene_changed = Signal()
    active_person_changed = Signal()
    def __init__(self,
                 person_selector:ActivePersonSelector,
                 processing_mode_selector:ProcessingModeSelector,
                 client_app:ClientApp,
                 scene_3d:AttentionScene3DService,
                 scene_initializer:AttentionSceneInitializerService,
                 gaze_callibration:PersonGazeCallibrationService,
                 gaze_estimation:PersonGazeEstimationService,
                 ) -> None:
        super().__init__()
        self._scene_3d = scene_3d
        self._processing_mode_selector = processing_mode_selector
        self._client_app = client_app
        self._cached_active_person:Person|None = None
        self._cached_active_scene:AttentionScene|None = None
        self._scene_initializer = scene_initializer
        self._gaze_callibration = gaze_callibration
        self._gaze_estimation = gaze_estimation
        self._person_selector = person_selector
        
        self._scene_initializer.attention_project_changed.connect(self._observe_project_changed)
        self._person_selector.active_person_changed.connect(self._observe_selector_active_person_changed)
        self._update_state_with_active_person()
        self._processing_mode_selector.running_mode_changed.connect(self._running_mode_changed)
        self._set_running_mode(self._processing_mode_selector.running_mode())

        self._scene_update_timer = QTimer()
        self._scene_update_timer.setInterval(50)
        self._scene_update_timer.setSingleShot(False)
        self._scene_update_timer.timeout.connect(self._scene_update_timer_timeouted)
        self._scene_update_timer.start()

    @Slot(ProcessingModeSelector.RunningMode)
    def _running_mode_changed(self, mode:ProcessingModeSelector.RunningMode):
        self._set_running_mode(mode)
    def _set_running_mode(self, mode:ProcessingModeSelector.RunningMode):
        self._client_app.set_enabled(mode == ProcessingModeSelector.RunningMode.Online)

    @Slot()
    def _scene_update_timer_timeouted(self):
        scene = self.active_scene()
        now = datetime.datetime.now()
        if scene:
            scene.trigger_update(now)

    def active_scene(self) -> AttentionScene|None:
        pr = self._scene_initializer.project()
        if not pr:
            return None
        return pr.scene()
    
    def active_person(self):
        self._person_selector.active_person()

    def active_person_selector(self) -> ActivePersonSelector:
        return self._person_selector

    def reset(self):
        self._person_selector.set_active_person(None)
        self._scene_initializer.set_project_data(None)

    @Slot()
    def _observe_project_changed(self):
        new_scene = self.active_scene()
        if new_scene != self._cached_active_scene and self._cached_active_scene is not None:
            self._cached_active_scene.timer().stop()

        if new_scene is not None:
            new_scene.timer().start()

        self._cached_active_scene = new_scene
        self._person_selector.set_active_person(None)
        self.active_scene_changed.emit()
        
    @Slot()
    def _observe_selector_active_person_changed(self):
        self._update_state_with_active_person()
        self.active_person_changed.emit()

    def _update_state_with_active_person(self):
        new_active_person = self.active_person()
        if self._cached_active_person == new_active_person:
            return
        old_active_person = self._cached_active_person
        self._cached_active_person = new_active_person
        self._gaze_callibration.reset_callibration()
        self._gaze_estimation.set_person(self._cached_active_person)

        print(f'{old_active_person=}')
        if old_active_person:
            self._scene_3d.set_tracking(old_active_person, False)
        print(f'{new_active_person=}')
        if new_active_person:
            self._scene_3d.set_tracking(new_active_person, True)
        
        self._gaze_estimation.set_person(self._cached_active_person)
