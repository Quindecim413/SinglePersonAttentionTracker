from common.collections.observing_items import Item, ItemsCollection
from web.domain.exposed_person import ExposedPerson
from PySide6.QtCore import QMimeData, Slot, Signal


class ClientForExposedPersonItem(Item):
    def __init__(self, exposed_person:ExposedPerson) -> None:
        super().__init__()
        self._exposed_person = exposed_person
        self._current_connected_client = exposed_person.client()
        if self._current_connected_client is None:
            self.remove_item()
            return
        
        self._exposed_person.client_changed.connect(self._exposed_person_client_changed)

    def exposed_person(self):
        return self._exposed_person
    
    def connected_client(self):
        return self._current_connected_client

    @Slot()
    def _exposed_person_client_changed(self):
        self.remove_item()


class ClientForExposedPersonCollection(ItemsCollection[ClientForExposedPersonItem]):
    def __init__(self, exposed_person:ExposedPerson) -> None:
        super().__init__()
        self._exposed_person = exposed_person
        
        self._exposed_person.client_changed.connect(self._exposed_person_client_changed)

        if self._exposed_person.client():
            self.add_item(ClientForExposedPersonItem(self._exposed_person))

    def exposed_person(self):
        return self._exposed_person

    @Slot()
    def _exposed_person_client_changed(self):
        if self._exposed_person.client():
            self.add_item(ClientForExposedPersonItem(self._exposed_person))
    
    def handle_mimedata(self, mimedata: QMimeData):
        return super().handle_mimedata(mimedata)