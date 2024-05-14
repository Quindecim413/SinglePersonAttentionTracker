from PySide6.QtCore import QObject, Slot, Signal

from common.domain.interfaces import Person
from web.domain.connected_client import ConnectedClient


class ExposedPerson(QObject):
    client_changed = Signal()

    def __init__(self, person:Person) -> None:
        super().__init__()
        self._person = person
        self._client:ConnectedClient|None = None

    def person(self) -> Person:
        return self._person
    
    def client(self) -> ConnectedClient|None:
        return self._client

    def set_connected_client(self, client:ConnectedClient|None):
        if self._client != client:
            if self._client:
                self._client.set_person(None)
                self._client.disconnect(self)
            
            self._client = client
            if self._client:
                self._client.set_person(self._person)
                self._client.connection_closed.connect(self._client_connection_closed)
            self.client_changed.emit()

    @Slot()
    def _client_connection_closed(self):
        self.set_connected_client(None)