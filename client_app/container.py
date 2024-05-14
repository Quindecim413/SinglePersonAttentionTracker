from multiprocessing import process
from pathlib import Path
from dependency_injector import providers, containers
import socketio
from client_app.callibration_page.container import CallibrationPageContainer
from client_app.camera_page.container import CameraPageContainer
from client_app.main.view import ClientMainWindow
from client_app.main.vm import ClientMainWindowVM
from client_app.offline_project_select_page.container import OfflineProjectSelectPageContainer
from client_app.person_select_page.container import PersonSelectPageContainer
from client_app.services.processing_mode_selector import ProcessingModeSelector

from client_app.tracking_page.container import TrackingPageContainer
from common.containers import CameraSourceContainer, SceneContainer
from PySide6.QtWidgets import QWidget
from common.domain.gaze.default_callibrator import DefaultEyesCallibrator
from common.domain.gaze.default_predictor import DefaultEyeDirectionPredictor
from common.domain.gaze.eyes_direction_predictor import EyesDirectionEstimator
from common.domain.gaze.head_data_estimator import HeadDataEstimator
from common.services.active_person import ActivePersonSelector
from common.services.active_work_state import ActiveWorkState
from common.services.face_scanning.face_scanner import FaceScannerService
from common.services.gaze.callibration import PersonGazeCallibrationService
from common.services.gaze.estimation import HeadDataEstimatorFactory, PersonGazeEstimationService
from common.widgets.project_data_select.container import ProjectDataSelectContainer
from web.apps.client.app import ClientApp


client_storage = Path(__file__).parent.parent / 'docs' / 'client'
projects_storage_dir = client_storage / 'projects'
archives_storage_dir = client_storage / 'archives'

class DefaultHeadDataEstimatorFactory(HeadDataEstimatorFactory):
    def __init__(self) -> None:
        super().__init__()

    def create_default(self) -> HeadDataEstimator:
        eyes_direction_estimator = EyesDirectionEstimator(DefaultEyeDirectionPredictor(), DefaultEyeDirectionPredictor(left_eye=False))
        eyes_direction_estimator.fit([])
        return HeadDataEstimator(eyes_direction_estimator)
    
    def create(self, eyes_direction_estimator: EyesDirectionEstimator) -> HeadDataEstimator:
        return HeadDataEstimator(eyes_direction_estimator)

class ClientAppContainer(containers.DeclarativeContainer):
    scene = providers.Container(SceneContainer,
                                storage_dir=projects_storage_dir)
    camera = providers.Container(CameraSourceContainer)
    face_scanner = providers.Singleton(FaceScannerService,
                                       video_service=camera.camera_service)

    head_data_estimator_factory = providers.Factory(DefaultHeadDataEstimatorFactory)

    eyes_callibrator = providers.Factory(DefaultEyesCallibrator)

    gaze_callibration = providers.Singleton(PersonGazeCallibrationService,
                                            eyes_callibrator=eyes_callibrator,
                                            face_scanner=face_scanner)
    
    gaze_estimation = providers.Singleton(PersonGazeEstimationService,
                                          callibration_service=gaze_callibration,
                                          face_scanner=face_scanner,
                                          head_data_estimator_factory=head_data_estimator_factory)
    
    processing_mode_selector = providers.Singleton(ProcessingModeSelector)
    person_selector = providers.Singleton(ActivePersonSelector)


    client_app = providers.Singleton(ClientApp,
                                     projects_archives_dir=archives_storage_dir,
                                     client=providers.Factory(socketio.AsyncClient),
                                     person_selector=person_selector,
                                     projects_repo=scene.repo,
                                     scene_initializer=scene.initializer)


    active_work_state = providers.Singleton(ActiveWorkState,
                                   client_app=client_app,
                                   processing_mode_selector=processing_mode_selector, 
                                   person_selector=person_selector,
                                   scene_3d=scene.scene_3d_service,
                                   scene_initializer=scene.initializer,
                                   gaze_callibration=gaze_callibration,
                                   gaze_estimation=gaze_estimation)

    empty_widget = providers.Factory(QWidget)

    select_project_container = providers.Container(ProjectDataSelectContainer,
                                                   scene=scene)

    offline_project_page_container = providers.Container(OfflineProjectSelectPageContainer,
                                                         scene=scene,
                                                         processing_mode_selector=processing_mode_selector,
                                                         select_project_container=select_project_container)

    person_select_page_container = providers.Container(PersonSelectPageContainer,
                                                       scene=scene,
                                                       active_person_selector=person_selector,
                                                       )
    
    camera_page_container = providers.Container(CameraPageContainer,
                                                camera_container=camera,
                                                face_scanner=face_scanner)

    callibration_page_container = providers.Container(CallibrationPageContainer,
                                                      scene_3d_service=scene.scene_3d_service,
                                                      gaze_callibration_service=gaze_callibration,
                                                      camera_container=camera)

    tracking_page_container = providers.Container(TrackingPageContainer,
                                                  active_work_state=active_work_state,
                                                  active_person_selector=person_selector)

    
    app_vm = providers.Factory(ClientMainWindowVM,
                               processing_mode_selector=processing_mode_selector,
                               scene_initializer=scene.initializer,
                               face_scanner=face_scanner,
                               video_service=camera.camera_service
                               )
    app_view = providers.Factory(ClientMainWindow,
                                   vm=app_vm, 
                                   camera_page=camera_page_container.page,
                                   networking_page=empty_widget,
                                   callibration_page=callibration_page_container.page,
                                   offline_project_select_page=offline_project_page_container.page,
                                   person_select_page=person_select_page_container.page,
                                   tracking_page=tracking_page_container.page,
                                   scene_window=scene.render_main_window)