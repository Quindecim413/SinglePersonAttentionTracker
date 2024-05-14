from PySide6.QtWidgets import QWidget
from dependency_injector import providers, containers

from common.dtos.calibration import CallibrationRecord
from common.services.gaze.callibration import PersonGazeCallibrationService
from common.services.scene.scene_3d import AttentionScene3DService
from common.widgets.preview_callibration import CallibrationRecordPreviewWidget
from .view import CallibrationPage, CallibrationPageVM, CallibrationRecordWidgetFactory


class DefaultCallibrationRecordWidgetFactory(CallibrationRecordWidgetFactory):
    def __call__(self, record: CallibrationRecord) -> QWidget:
        return CallibrationRecordPreviewWidget(record)


class CallibrationPageContainer(containers.DeclarativeContainer):
    gaze_callibration_service = providers.Dependency(instance_of=PersonGazeCallibrationService)
    camera_container = providers.DependenciesContainer()
    scene_3d_service = providers.Dependency(instance_of=AttentionScene3DService)
    callibration_record_widget_factory = providers.Factory(DefaultCallibrationRecordWidgetFactory)
    
    page_vm = providers.Factory(CallibrationPageVM,
                                scene_3d_service=scene_3d_service,
                                gaze_callibration_service=gaze_callibration_service)
    page = providers.Factory(CallibrationPage,
                             vm=page_vm,
                             callibration_record_preview_widget_factory=callibration_record_widget_factory)
