from datetime import timedelta
from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtGui import QCloseEvent, QMouseEvent, QPainter, QColor,QBrush
from PySide6.QtWidgets import QMainWindow, QWidget, QToolBar, QLabel, QFrame, QSizePolicy,\
    QSplitter, QScrollArea, QVBoxLayout, QPushButton, QLineEdit, QDoubleSpinBox, QSpinBox, QGridLayout, QHBoxLayout

from common.domain.interfaces import SceneObj




class SceneObjPreviewWidget(QWidget):
    def __init__(self, scene_obj:SceneObj, parent=None) -> None:
        super().__init__(parent)
        self.scene_obj = scene_obj
        self.scene_obj.removed_from_scene.connect(self._handle_model_removed)
        self.scene_obj.element_name_changed.connect(self._handle_model_scene_obj_name_changed)
        self.scene_obj.is_selected_changed.connect(self._handle_model_selected_changed)
        self._name = QLabel(self.scene_obj.element_name())
        self._name.setToolTip(self.scene_obj.element_name())
        self._name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._select_btn = QPushButton('')
        self._select_btn.setFixedSize(15, 15)
        self._select_btn.clicked.connect(self._toggle_selection_clicked)
        

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(self._select_btn)
        hbox.addWidget(self._name)
        self.setLayout(hbox)
        self._handle_model_selected_changed(self.scene_obj.is_selected())
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    @Slot()
    def _handle_model_removed(self):
        self.setEnabled(False)

    @Slot(bool)
    def _handle_model_selected_changed(self, selected):
        if selected:
            self._select_btn.setStyleSheet('background-color: #fcf403;')
        else:
            self._select_btn.setStyleSheet('')
    
    @Slot()
    def _toggle_selection_clicked(self):
        self.scene_obj.set_selected(not self.scene_obj.is_selected())

    @Slot(str)
    def _handle_model_scene_obj_name_changed(self, name):
        self._name.setText(name)
        self._name.setToolTip(self.scene_obj.element_name())