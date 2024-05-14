from dataclasses import dataclass
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage
from PySide6.QtMultimedia import QMediaCaptureSession, QVideoSink, QVideoFrame, QCameraDevice, QCamera


class VideoService(QObject):
    @dataclass
    class TimestampedFrame:
        timestamp:datetime
        frame:QVideoFrame
    
    is_available_changed = Signal(bool)
    
    played = Signal()
    paused = Signal()
    stopped = Signal()

    video_rotation_angle_changed = Signal(QVideoFrame.RotationAngle)
    is_mirrored_changed = Signal(bool)
    error_occured = Signal(str)
    frame_changed = Signal(TimestampedFrame)
    source_description_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._do_mirror = False
        self._capture_rotation_angle = QVideoFrame.RotationAngle.Rotation0

    def source_description(self) -> str:
        raise NotImplementedError()

    def play(self) -> None:
        raise NotImplementedError()

    def pause(self) -> None:
        raise NotImplementedError()
    
    def stop(self) -> None:
        raise NotImplementedError()

    def is_available(self) -> bool:
        raise NotImplementedError()

    def is_paused(self) -> bool:
        raise NotImplementedError()

    def video_sink(self) -> QVideoSink:
        raise NotImplementedError()

    def rotate_clockwise(self):
        print('rotate_clockwise')
        match self._capture_rotation_angle :
            case QVideoFrame.RotationAngle.Rotation0:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation90)
            case QVideoFrame.RotationAngle.Rotation90:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation180)
            case QVideoFrame.RotationAngle.Rotation180:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation270)
            case QVideoFrame.RotationAngle.Rotation270:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation0)
    
    def rotate_counter_clockwise(self):
        print('rotate_counter_clockwise')
        match self._capture_rotation_angle :
            case QVideoFrame.RotationAngle.Rotation0:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation270)
            case QVideoFrame.RotationAngle.Rotation90:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation0)
            case QVideoFrame.RotationAngle.Rotation180:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation90)
            case QVideoFrame.RotationAngle.Rotation270:
                self.set_rotation_angle(QVideoFrame.RotationAngle.Rotation180)

    def set_rotation_angle(self, rotation_angle: QVideoFrame.RotationAngle):
        assert isinstance(rotation_angle, QVideoFrame.RotationAngle)
        if rotation_angle != self._capture_rotation_angle:
            self._capture_rotation_angle = rotation_angle
            self.video_rotation_angle_changed.emit(self._capture_rotation_angle)
    
    def set_mirrored(self, value: bool):
        value = bool(value)
        if value != self._do_mirror:
            self._do_mirror = value
            self.is_mirrored_changed.emit(self._do_mirror)
    
    def is_mirrored(self):
        return self._do_mirror