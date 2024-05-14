from enum import Enum
from PySide6.QtCore import QObject, Slot, Signal


class ProcessingModeSelector(QObject):
    class RunningMode(Enum):
        Offline = 'offline'
        Online = 'online'
    
    running_mode_changed = Signal(RunningMode)
    
    def __init__(self, ) -> None:
        super().__init__()
        self._running_mode = ProcessingModeSelector.RunningMode.Offline
        
    def running_mode(self) -> RunningMode:
        return self._running_mode

    def set_online_mode(self):
        if self._running_mode != ProcessingModeSelector.RunningMode.Online:
            self._running_mode = ProcessingModeSelector.RunningMode.Online
            self.running_mode_changed.emit(self._running_mode)

    def set_offline_mode(self):
        if self._running_mode != ProcessingModeSelector.RunningMode.Offline:
            self._running_mode = ProcessingModeSelector.RunningMode.Offline
            self.running_mode_changed.emit(self._running_mode)