from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from common.utils import clear_layout
from common.widgets.preview_person import PersonPreviewWidget
from web.domain.connected_client import ConnectedClient
from web.domain.exposed_person import ExposedPerson
from web.widgets.preview_connected_client import ConnectedClientPreviewWidget


class ExposedPersonPreviewWidget(QWidget):
    def __init__(self, exposed_person:ExposedPerson) -> None:
        super().__init__()
        self._exposed_person = exposed_person

        self._connected_client_layout = QVBoxLayout()
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Модель оператора:'))
        vbox.addWidget(PersonPreviewWidget(self._exposed_person.person()))
        vbox.addWidget(QLabel('Клиент:'))
        vbox.addLayout(self._connected_client_layout)
        self.setLayout(vbox)
        
        self.set_client(self._exposed_person.client())

    @Slot()
    def _observe_connected_client_changed(self):
        self.set_client(self._exposed_person.client())

    def set_client(self, client:ConnectedClient|None):
        clear_layout(self._connected_client_layout)
        if client:
            preview_widget:QWidget = ConnectedClientPreviewWidget(client)
        else:
            preview_widget = QLabel('Не установлен')

        self.layout().addWidget(preview_widget)
