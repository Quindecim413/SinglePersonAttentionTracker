from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout
from dependency_injector import providers, containers
from common.containers import SceneContainer
from common.widgets.project_data_select.container import ProjectDataSelectContainer
from common.widgets.project_data_select.widget import ProjectDataSelectionWidget, ProjectDataWidgetFactory
from client_app.offline_project_select_page.view import OfflineSelectProjectPage, OfflineSelectProjectPageVM
from client_app.services.processing_mode_selector import ProcessingModeSelector
from common.vms.project_loading import ProjectImportVM



class OfflineProjectSelectPageContainer(containers.DeclarativeContainer):
    scene:SceneContainer = providers.DependenciesContainer() #type:ignore
    processing_mode_selector = providers.Dependency(instance_of=ProcessingModeSelector)
    select_project_container:ProjectDataSelectContainer = providers.DependenciesContainer() #type:ignore

    page_vm = providers.Factory(OfflineSelectProjectPageVM,
                                processing_mode_selector=processing_mode_selector)
    
    project_import_vm = providers.Factory(ProjectImportVM,
                                          scene_initializer=scene.initializer,
                                          projects_repo=scene.repo)

    page = providers.Factory(OfflineSelectProjectPage,
                             vm=page_vm,
                             project_import_vm=project_import_vm,
                             select_project_data_widget=select_project_container.select_widget)
