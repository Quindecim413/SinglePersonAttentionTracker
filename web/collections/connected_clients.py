from PySide6.QtCore import QMimeData, QObject, Signal, Slot

from common.collections.observing_items import Item, ItemsCollection
from web.domain.connected_client import ConnectedClient
from web.dtos.connected_client_data import ConnectedClientData, ConnectedClientDataAdapter


class ConnectedClientItem(Item):
    def __init__(self, connected_client:ConnectedClient) -> None:
        super().__init__()
        self._connected_client = connected_client
        self._connected_client.connection_closed.connect(self._client_connection_closed)
        if not self._connected_client.is_connected():
            self.remove_item()

    def client(self) -> ConnectedClient:
        return self._connected_client

    @Slot()
    def _client_connection_closed(self):
        self.remove_item()
    
    def make_mimedata(self) -> QMimeData | None:
        data = ConnectedClientDataAdapter.dump_json(ConnectedClientData(self._connected_client.sid())).decode()
        mime = QMimeData()
        mime.setText(data)
        return mime

class ConnectedClientsCollection(ItemsCollection[ConnectedClientItem]):
    def __init__(self) -> None:
        super().__init__()

    def add_client(self, client:ConnectedClient):
        self.add_item(ConnectedClientItem(client))

    def clients(self):
        return [item.client() for item in self.items()]
    
    def get_by_sid(self, sid:str):
        return next(filter(lambda c:c.sid() == sid, self.clients()), None)

    # def __getitem__(self, sid):
    #     for client in self.clients()
