from PySide6.QtCore import QObject, Slot, Signal
from common.domain.interfaces import AttentionScene

from common.services.scene.project_data import AttentionProjectData


class AttentionProject(QObject):
    removed = Signal()

    def __init__(self, 
                 project_data:AttentionProjectData,
                 scene:AttentionScene) -> None:
        super().__init__()
        self._project_data = project_data
        self._project_data.removed.connect(self._project_data_removed)
        self._scene = scene
    
    @Slot()
    def _project_data_removed(self):
        self.removed.emit()

    def scene(self):
        return self._scene
    
    def project_data(self):
        return self._project_data
    
    def save(self):
        self._project_data.set_description(self._scene.export_description())
        self._project_data.save()
