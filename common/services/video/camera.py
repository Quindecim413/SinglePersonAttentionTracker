from datetime import datetime
from PySide6.QtCore import QObject, Slot, Signal
from .types import VideoService
from PySide6.QtMultimedia import QMediaCaptureSession, QVideoSink, QVideoFrame, QCameraDevice, QCamera,QMediaDevices


class CameraService(VideoService):
    camera_device_changed = Signal(QCameraDevice)
    def __init__(self, ) -> None:
        super().__init__()
        self._capture_session = QMediaCaptureSession(self)
        self._private_video_sink = QVideoSink(self)
        self._exposed_video_sink = QVideoSink(self)
        
        self._capture_session.setVideoSink(self._private_video_sink)
        self._camera = QCamera(QMediaDevices.defaultVideoInput(), parent=self)
        self._camera.errorOccurred.connect(self._observe_camera_error_occured)
        self._camera.activeChanged.connect(self._observe_camera_active_changed)
        self._camera.cameraDeviceChanged.connect(self._observe_camera_device_changed)

        self._capture_session.setCamera(self._camera)
        self._capture_session.videoSink().videoFrameChanged.connect(self._frame_changed)
        self._do_mirror = False
        self._capture_rotation_angle = QVideoFrame.RotationAngle.Rotation0

        self._is_available = not self._camera.cameraDevice().isNull()

    def set_device(self, device:QCameraDevice):
        if device != self._camera.cameraDevice():
            self._camera.setCameraDevice(device)
            self.source_description_changed.emit(self.source_description())

    def source_description(self):
        return self._camera.cameraDevice().description()

    def device(self):
        return self._camera.cameraDevice()

    @Slot(QCamera.Error, str)
    def _observe_camera_error_occured(self, err, msg):
        old_is_available = self._is_available
        if err == QCamera.Error.CameraError:
            self.error_occured.emit(msg)
            self._is_available = False
        else:
            self._is_available = self._camera.cameraDevice().isNull()
        
        if old_is_available != self._is_available:
            self.is_available_changed.emit(self._is_available)

    @Slot(bool)
    def _observe_camera_active_changed(self, is_active:bool):
        self.is_available_changed.emit(self.is_available())
        if is_active:
            self.played.emit()
        else:
            self.paused.emit()
            self.stopped.emit()

    @Slot(QCameraDevice)
    def _observe_camera_device_changed(self, device:QCameraDevice):
        self.camera_device_changed.emit(device)
        old_is_available = self._is_available
        self._is_available = not device.isNull()
        
        if old_is_available != self._is_available:
            self.is_available_changed.emit(self._is_available)

    def play(self):
        if self.is_available() and not self._camera.isActive():
            self._camera.start()

    def stop(self):
        if self.is_available() and not self.is_paused():
            self._camera.stop()
        # print('self.camera.error() ', self._camera.error() )
        # if self._camera.error() == QCamera.Error.NoError:
        #     try:
        #         if self._camera.isAvailable() and self._camera.isActive():
        #             self._camera.stop()  
        #     except:
        #         pass
        # elif self._camera.error() == QCamera.Error.CameraError:
        #     self._camera.stop()
    
    def pause(self):
        self.stop()

    def is_available(self) -> bool:
        return not self._camera.cameraDevice().isNull() and self._camera.isAvailable() and self._camera.error() == QCamera.Error.NoError

    def is_paused(self) -> bool:
        if not self.is_available():
            return True
        return not self._camera.isActive()

    def video_sink(self) -> QVideoSink:
        return self._exposed_video_sink

    @Slot(QVideoFrame)
    def _frame_changed(self, frame: QVideoFrame):
        frame.setMirrored(self._do_mirror)
        frame.setRotationAngle(self._capture_rotation_angle)
        self._exposed_video_sink.setVideoFrame(frame)
        self.frame_changed.emit(VideoService.TimestampedFrame(datetime.now(), frame))