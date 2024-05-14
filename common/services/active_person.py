from PySide6.QtCore import QObject, Slot, Signal
from common.domain.interfaces import Person


class ActivePersonSelector(QObject):
    active_person_changed = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self._active_person:Person|None = None

    def active_person(self) -> Person|None:
        return self._active_person

    def set_active_person(self, person:Person|None) -> None:
        if person != self._active_person:
            self._active_person = person
            self.active_person_changed.emit()    

    @Slot()
    def clear_selection(self)->None:
        self.set_active_person(None)

