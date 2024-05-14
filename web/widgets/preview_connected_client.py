from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from common.domain.interfaces import Person
from web.domain.connected_client import ConnectedClient


class ConnectedClientPreviewWidget(QWidget):
    def __init__(self, client:ConnectedClient) -> None:
        super().__init__()
        self._client = client

        sid_label = QLabel(self._client.sid())
        self._name_lbl = QLabel(self._client.name())
        self._person_info_lbl = QLabel()

        grid = QGridLayout()
        grid.addWidget(QLabel('# клиента'), 0,0)
        grid.addWidget(sid_label, 0,1)
        grid.addWidget(QLabel('Имя'), 1,0)
        grid.addWidget(self._name_lbl, 1,1)
        grid.addWidget(QLabel('Оператор:'), 2, 0)
        grid.addWidget(self._person_info_lbl, 2, 1)

        self.setLayout(grid)


        self._client.connection_closed.connect(self._observe_connection_closed)

        self._set_is_connected(self._client.is_connected())
        self._set_person(self._client.person())

    @Slot()
    def _observe_connection_closed(self):
        self._set_is_connected(False)

    def _set_is_connected(self, is_connected:bool):
        self.setEnabled(is_connected)

    def _set_person(self, person:Person|None):
        if person is None:
            self._person_info_lbl.setText('Не выбран')
        else:
            self._person_info_lbl.setText(f'#{person.element_id()}: {person.element_name()}')
