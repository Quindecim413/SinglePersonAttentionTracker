from __future__ import annotations
from PySide6.QtCore import Slot, Signal, QObject
from common.collections.projects import ProjectsDataCollection
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.repo import AttentionProjectsRepo


class ProjectsPageVM(QObject):
    def __init__(self,
                 attention_projects_repo:AttentionProjectsRepo,
                 scene_initializer:AttentionSceneInitializerService) -> None:
        super().__init__()
        self._projects_data_collection = ProjectsDataCollection(attention_projects_repo, scene_initializer)

    def projects_data_collection(self) -> ProjectsDataCollection:
        return self._projects_data_collection

    
