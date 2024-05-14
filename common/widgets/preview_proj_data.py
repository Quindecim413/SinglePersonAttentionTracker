from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.project import AttentionProject

from common.services.scene.project_data import AttentionProjectData


class ProjectDataPreviewWidget(QWidget):
    def __init__(self,
                 project_data:AttentionProjectData,
                 scene_initializer:AttentionSceneInitializerService,
                 parent=None
                 ) -> None:
        super().__init__(parent)
        self.project_data = project_data
        self.scene_initializer = scene_initializer

        

        self._id_lbl = QLabel(self.project_data.project_id())
        self._name_lbl = QLabel(self.project_data.name())
        self._name_lbl.setWordWrap(True)
        self._time_created_lbl = QLabel(self.project_data.creation_date().isoformat())
        self._store_directory = QLineEdit()
        self._store_directory.setReadOnly(True)
        self._store_directory.setText(str(self.project_data.storage().project_folder.resolve()))

        grid = QGridLayout()
        grid.addWidget(QLabel('Сцена #'), 0, 0)
        grid.addWidget(self._id_lbl, 0, 1)
        grid.addWidget(QLabel('Название'), 1, 0)
        grid.addWidget(self._name_lbl, 1, 1)
        self.setLayout(grid)

        self.scene_initializer.attention_project_changed.connect(self._observe_attention_project_changed)
        self.project_data.name_changed.connect(self._name_changed)

    @Slot()
    def _observe_attention_project_changed(self):
        self._setup_backgroud()

    def _setup_backgroud(self):
        project = self.scene_initializer.project()
        if project and self.project_data.project_id() == project.project_data().project_id():
            self.setStyleSheet("""
                QWidget {
                    background-color: #DCE6F1;
                    border: 2px solid #5E9CEA;
                }
            """)
        else:
            self.setStyleSheet("")

    @Slot(str)
    def _name_changed(self, name):
        self._name_lbl.setText(name)



