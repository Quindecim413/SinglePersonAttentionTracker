from pathlib import Path
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,QScrollArea, QSizePolicy, QGridLayout
from PySide6.QtGui import QIcon

from common.utils import clear_layout
from common.widgets.preview_person import PersonPreviewWidget
from web.collections.connected_clients import ConnectedClientsCollection
from web.domain.connected_client import ConnectedClient
from web.domain.exposed_person import ExposedPerson
from web.dtos.connected_client_data import ConnectedClientDataAdapter
from web.widgets.exposed_person_info import ExposedPersonInfoWidget
from web.widgets.preview_connected_client import ConnectedClientPreviewWidget


class _ConnectedClientFrame(QFrame):
    def __init__(self, exposed_person:ExposedPerson, 
                 connected_clients_collection:ConnectedClientsCollection) -> None:
        super().__init__()
        self._exposed_person = exposed_person
        self._connected_clients_collection = connected_clients_collection
        
        self.setAcceptDrops(True)
        # self.setMinimumHeight(40)
        # self.setMaximumWidth(60)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background-color:rgb(217, 217, 217);")
        self.setLineWidth(4)
        # self.setBor
        self._vbox = QVBoxLayout()

        self.setLayout(self._vbox)

        self._exposed_person.client_changed.connect(self._observe_connected_client_changed)

        self._set_connected_client(self._exposed_person.client())

    @Slot()
    def _observe_connected_client_changed(self):
        self._set_connected_client(self._exposed_person.client())

    def _set_connected_client(self, client:ConnectedClient|None):
        clear_layout(self._vbox)
        if client:
            preview_widget:QWidget = ConnectedClientPreviewWidget(client)
            
        else:
            preview_widget = QLabel('Перетащите сюда клиента')
        self._vbox.addWidget(preview_widget)
        self.updateGeometry()


    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasText():
            try:
                client_sid = ConnectedClientDataAdapter.validate_json(mime.text()).sid
                client = self._connected_clients_collection.get_by_sid(client_sid)
                if client:
                    event.acceptProposedAction()
                    self._exposed_person.set_connected_client(client)
                    
            except:
                event.ignore()
                return


class ConfigureExposedPersonWidget(QWidget):
    def __init__(self, exposed_person:ExposedPerson, 
                 connected_clients_collection:ConnectedClientsCollection) -> None:
        super().__init__()
        self._exposed_person = exposed_person
        self._connected_clients_collection = connected_clients_collection
        
        person_preview = PersonPreviewWidget(self._exposed_person.person())
        self._connected_client_frame = _ConnectedClientFrame(self._exposed_person, self._connected_clients_collection)
        # self._connected_client_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._show_more_btn = QPushButton('Подробнее')
        # self._show_more_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._show_more_btn.clicked.connect(self._show_more_clicked)

        remove_btn = QPushButton()
        remove_btn.setIcon(QIcon(str(Path(__file__).parent / 'src/trash.png')))
        remove_btn.clicked.connect(self._remove_btn_clicked)
        remove_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # grid = QGridLayout()
        # grid.addWidget(person_preview, 0, 0)
        # grid.addWidget(self._show_more_btn, 0, 1)

        # grid.addWidget(self._connected_client_frame, 1, 0)
        # grid.addWidget(remove_btn, 1, 1)

        # grid.setColumnStretch(0, 1)
        # grid.setRowStretch(1, 1)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(person_preview)
        hbox1.addWidget(self._show_more_btn)

        hbox1.setContentsMargins(1, 1, 1, 1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self._connected_client_frame)
        hbox2.addWidget(remove_btn)
        hbox2.setContentsMargins(1, 1, 1, 1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

    @Slot()
    def _remove_btn_clicked(self):
        self._exposed_person.set_connected_client(None)

    @Slot()
    def _show_more_clicked(self):
        self._show_widget = QScrollArea()
        self._show_widget.setWidget(ExposedPersonInfoWidget(self._exposed_person))
        self._show_widget.setWidgetResizable(True)
        self._show_widget.show()
        

    

    