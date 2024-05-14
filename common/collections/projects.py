from PySide6.QtCore import QMimeData, QObject, Slot, Signal
from common.collections.observing_items import Item, ItemsCollection
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.project import AttentionProject
from common.services.scene.project_data import AttentionProjectData

from common.services.scene.repo import AttentionProjectsRepo


class AvailableProjectDataItem(Item):
    is_loaded_changed = Signal(bool)
    def __init__(self,
                 project_data:AttentionProjectData,
                 scene_initializer:AttentionSceneInitializerService) -> None:
        super().__init__()
        self._project_data = project_data
        self._scene_initializer = scene_initializer
        self._project_data.removed.connect(self._project_data_removed)
        self._scene_initializer.attention_project_changed.connect(self._observe_attention_project_changed)
        self._old_project_loaded = self.is_loaded()
    

    def project_data(self):
        return self._project_data

    def _update_project_loaded(self, is_loaded):
        if self._old_project_loaded != is_loaded:
            self._old_project_loaded = is_loaded
            self.is_loaded_changed.emit(is_loaded)

    @Slot()
    def _observe_attention_project_changed(self):
        self._update_project_loaded(self.is_loaded())

    @Slot()
    def _project_data_removed(self):
        self.remove_item()


    def make_mimedata(self) -> QMimeData:
        mime = QMimeData()
        mime.setText(self._project_data.project_id())
        return mime

    def load_project(self):
        self._scene_initializer.set_project_data(self._project_data)

    def is_loaded(self) -> bool:
        if proj:=self._scene_initializer.project():
            return proj.project_data().project_id() == self._project_data.project_id()
        return False


class ProjectsDataCollection(ItemsCollection[AvailableProjectDataItem]):
    def __init__(self,
                 projects_repo:AttentionProjectsRepo,
                 scene_initializer:AttentionSceneInitializerService
                 ) -> None:
        super().__init__()
        self._scene_initializer = scene_initializer
        self._projects_repo = projects_repo
        self._projects_repo.project_data_imported.connect(self._observe_project_imported)
        for proj_data in self._projects_repo.projects_data():
            self.add_item(AvailableProjectDataItem(proj_data, self._scene_initializer))

    @Slot(AttentionProjectData)
    def _observe_project_imported(self, project_data:AttentionProjectData):
        self.add_item(AvailableProjectDataItem(project_data, self._scene_initializer))

    def handle_mimedata(self, mime:QMimeData):
        if not mime.hasText():
            return
        text = mime.text()
        maybe_project_data = self._projects_repo.get_project_data_by_id(text)
        if maybe_project_data is None:
            return
        if active_project:=self._scene_initializer.project():
            if maybe_project_data.project_id() == active_project.project_data().project_id():
                self._scene_initializer.set_project_data(None)


class SelectedProjectDataItem(Item):
    def __init__(self,
                 project_data:AttentionProjectData,
                 scene_initializer:AttentionSceneInitializerService) -> None:
        super().__init__()
        self._project_data = project_data
        self._scene_initializer = scene_initializer
        self._scene_initializer.attention_project_changed.connect(self._observe_project_changed)
    
    def project_data(self):
        return self._project_data

    @Slot()
    def _observe_project_changed(self):
        project = self._scene_initializer.project()
        if not project:
            self.remove_item()
        elif self._project_data.project_id() != project.project_data().project_id():
            self.remove_item()

    def make_mimedata(self) -> QMimeData:
        mime = QMimeData()
        mime.setText(self._project_data.project_id())
        return mime
    
    def unload_project(self,):
        self._scene_initializer.set_project_data(None)


class ActiveProjectDataCollection(ItemsCollection[SelectedProjectDataItem]):
    def __init__(self,
                 projects_repo:AttentionProjectsRepo,
                 scene_initializer:AttentionSceneInitializerService) -> None:
        super().__init__()
        self._projects_repo = projects_repo
        self._scene_initializer = scene_initializer
        self._scene_initializer.attention_project_changed.connect(self._observe_project_changed)
        if (proj:=self._scene_initializer.project()) is not None:
            self.add_item(SelectedProjectDataItem(proj.project_data(),
                                                self._scene_initializer))

    @Slot()
    def _observe_project_changed(self):
        project = self._scene_initializer.project()
        if project:
            self.add_item(SelectedProjectDataItem(project.project_data(), self._scene_initializer))

    def handle_mimedata(self, mime:QMimeData):
        if not mime.hasText():
            return
        text = mime.text()
        maybe_project_data = self._projects_repo.get_project_data_by_id(text)
        if not maybe_project_data:
            return
        self._scene_initializer.set_project_data(maybe_project_data)