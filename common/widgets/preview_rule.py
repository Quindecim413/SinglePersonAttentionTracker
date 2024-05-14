from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout

from common.domain.interfaces import AttentionRule


class AttentionRulePreviewWidget(QWidget):
    def __init__(self, attention_rule:AttentionRule, parent=None) -> None:
        super().__init__(parent)
        self.rule = attention_rule
        self.rule.removed_from_scene.connect(self._handle_removed)

        self.rule.element_name_changed.connect(self.observe_name_changed)
        self.rule.is_selected_changed.connect(self._observe_selected_changed)
        self._name = QLabel(self.rule.element_name())
        self._name.setToolTip(self.rule.element_name())
        
        self._select_btn = QPushButton('')
        self._select_btn.setFixedSize(15, 15)
        self._select_btn.clicked.connect(self._toggle_selection_clicked)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(self._select_btn)
        hbox.addWidget(self._name)
        self.setLayout(hbox)
        self._observe_selected_changed(self.rule.is_selected())

    @Slot()
    def _handle_removed(self):
        self.setEnabled(False)

    @Slot(bool)
    def _observe_selected_changed(self, selected):
        if selected:
            self._select_btn.setStyleSheet('background-color: #fcf403;')
        else:
            self._select_btn.setStyleSheet('')
    
    @Slot()
    def _toggle_selection_clicked(self):
        self.rule.set_selected(not self.rule.is_selected())

    @Slot(str)
    def observe_name_changed(self, name):
        self._name.setText(name)
        self._name.setToolTip(self.rule.element_name())

