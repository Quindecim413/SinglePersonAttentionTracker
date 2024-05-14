from abc import abstractmethod
from PySide6.QtCore import QObject, Slot, Signal, QTimer
from datetime import datetime


class SceneUpdateTimer(QObject):
    triggered_scene_update = Signal()
    @abstractmethod
    def now(self) -> datetime:
        ...

    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...


class RealTimeSceneUpdateTimer(SceneUpdateTimer):
    def __init__(self, ) -> None:
        super().__init__()
        self._frame_time = datetime.now()
        self._timer = QTimer()
        self._timer.setInterval(50)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._timeout)
        
    @Slot()
    def _timeout(self):
        self._frame_time = datetime.now()
        self.triggered_scene_update.emit()

    def start(self) -> None:
        return self._timer.start()
    
    def stop(self) -> None:
        return self._timer.stop()

    def now(self) -> datetime:
        return self._frame_time