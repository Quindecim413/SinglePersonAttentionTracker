from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout
from dependency_injector import providers, containers
from common.widgets.project_data_select.widget import ProjectDataSelectionWidget, ProjectDataWidgetFactory
from client_app.services.processing_mode_selector import ProcessingModeSelector
from common.collections.projects import ActiveProjectDataCollection, ProjectsDataCollection
from common.services.scene.project_data import AttentionProjectData
from common.widgets.preview_proj_data import ProjectDataPreviewWidget


class DefaultProjectDataWidgetFactory(ProjectDataWidgetFactory):
    def __init__(self, project_data_widget_provider:providers.Provider[ProjectDataPreviewWidget]) -> None:
        super().__init__()
        self.project_data_widget_provider = project_data_widget_provider

    def __call__(self, /, project_data: AttentionProjectData) -> QWidget:
        w = self.project_data_widget_provider(project_data=project_data)
        return w
        frame = QFrame()
        vbox = QVBoxLayout()
        vbox.addWidget(w)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setLayout(vbox)
        frame.setLineWidth(1)
        frame.setStyleSheet('background-color: #f0f0f0;')
        return frame


class ProjectDataSelectContainer(containers.DeclarativeContainer):
    scene = providers.DependenciesContainer()
    
    project_data_widget = providers.Factory(ProjectDataPreviewWidget,
                                            scene_initializer=scene.initializer)
    
    project_data_widget_factory = providers.Factory(DefaultProjectDataWidgetFactory,
                                                    project_data_widget_provider=project_data_widget.provider)
    
    project_data_collection = providers.Factory(ProjectsDataCollection,
                                                projects_repo=scene.repo,
                                                scene_initializer=scene.initializer)
    
    active_project_data_collection = providers.Factory(ActiveProjectDataCollection,
                                                       projects_repo=scene.repo,
                                                       scene_initializer=scene.initializer)
    select_widget = providers.Factory(ProjectDataSelectionWidget,
                                                   projects_data_collection=project_data_collection,
                                                   active_project_data_collection=active_project_data_collection,
                                                   short_project_data_widget_factory=project_data_widget_factory,
                                                   expanded_project_data_widget_factory=project_data_widget_factory)