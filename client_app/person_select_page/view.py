from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox

from common.domain.interfaces import Person
from common.services.active_person import ActivePersonSelector
from common.services.active_work_state import ActiveWorkState


class SelectPersonPage(QWidget):
    def __init__(self, 
                 select_person_widget:QWidget) -> None:
        super().__init__()
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Укажите используемого пользователя'))
        vbox.addWidget(select_person_widget)
        self.setLayout(vbox)
