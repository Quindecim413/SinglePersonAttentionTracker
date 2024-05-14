from PySide6.QtCore import QObject, Slot, Signal

from common.domain.interfaces import Person
from common.dtos.head_data import HeadData
from common.dtos.hits import PerformedRayCastResult


class ConnectedClient(QObject):
    person_changed = Signal()
    name_changed = Signal(str)
    connection_closed = Signal()
    
    def __init__(self, 
                 sid:str) -> None:
        super().__init__()
        self._sid = sid
        self._name:str = ''
        self._person:Person|None = None
        self._is_connected = True

    def sid(self):
        return self._sid

    def name(self)->str:
        return self._name

    def set_name(self, name:str):
        if self._name != name:
            self._name = name            
            self.name_changed.emit(name)

    def set_person(self, person:Person|None):
        if self._person != person:
            self._person = person
            self.person_changed.emit()
    
    def person(self)->Person|None:
        return self._person
    
    def set_head_data(self, head_data:HeadData):
        if p:=self._person:
            p.set_head_data(head_data)

    def set_performed_ray_cast_result(self, cast_result:PerformedRayCastResult):
        if p:=self._person:
            p.set_performed_ray_cast_result(cast_result)

    def is_connected(self) -> bool:
        return self._is_connected

    def notify_connection_closed(self):
        self._is_connected = False
        self.connection_closed.emit()
