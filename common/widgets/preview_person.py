from typing import Callable
from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtGui import QPainter, QColor,QBrush
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout

from common.domain.interfaces import Person


class CircleWidget(QWidget):
    def __init__(self, parent=None):
        super(CircleWidget, self).__init__(parent)
        self.color = QColor('red')  # Initial color of the circle

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))

        # Assuming you want a circle with a radius of 50 
        radius = 5
        center = self.rect().center()
        painter.drawEllipse(center, radius, radius)

    def sizeHint(self) -> QSize:
        return QSize(15, 15)

    def set_color(self, color:QColor):
        self.color = QColor(color)
        self.update()  # This will trigger a repaint


class PersonPreviewWidget(QWidget):
    def __init__(self, person:Person, parent=None) -> None:
        super().__init__(parent)
        self.person = person
        self.person.removed_from_scene.connect(self._handle_model_removed)

        self.person.element_name_changed.connect(self._handle_model_person_name_changed)
        self.person.head_color_changed.connect(self._handle_model_head_color_changed)
        self.person.is_selected_changed.connect(self._handle_model_selected_changed)
        self._name = QLabel(self.person.element_name())
        self._name.setToolTip(self.person.element_name())
        self._circle = CircleWidget()
        self._circle.set_color(self.person.head_color())

        self._select_btn = QPushButton('')
        self._select_btn.setFixedSize(15, 15)
        self._select_btn.clicked.connect(self._toggle_selection_clicked)

        
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(self._circle)
        hbox.addWidget(self._select_btn)
        hbox.addWidget(self._name)
        self.setLayout(hbox)
        self._handle_model_selected_changed(self.person.is_selected())

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
        self.person.set_selected(not self.person.is_selected())

    @Slot(tuple)
    def _handle_model_head_color_changed(self):
        self._circle.set_color(self.person.head_color())

    @Slot(str)
    def _handle_model_person_name_changed(self, name):
        self._name.setText(name)
        self._name.setToolTip(self.person.element_name())