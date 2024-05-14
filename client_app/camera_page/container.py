from dependency_injector import providers, containers

from client_app.camera_page.view import CameraPage
from common.services.face_scanning.face_scanner import FaceScannerService

class CameraPageContainer(containers.DeclarativeContainer):
    camera_container = providers.DependenciesContainer()
    face_scanner = providers.Dependency(instance_of=FaceScannerService)

    page = providers.Factory(CameraPage,
                             face_scanner=face_scanner,
                             camera_configure_widget=camera_container.camera_configure_widget)