from PySide6.QtCore import Qt, Slot, Signal, QObject, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QVideoFrame
from ..services.video.types import VideoService


class VideoPreviewWidget(QWidget):
    def __init__(self, video_service:VideoService) -> None:
        super().__init__()
        self.video_service = video_service
        self.setup_ui()

        self.video_service.is_available_changed.connect(self._observe_is_active_changed)
        self.video_service.paused.connect(self._observe_paused)
        self.video_service.played.connect(self._observe_played)

        self._set_active(self.video_service.is_available())
        self._set_paused(self.video_service.is_paused())

        self.video_service.video_sink().videoFrameChanged.connect(self._observe_video_frame_changed)

    @Slot(QVideoFrame)
    def _observe_video_frame_changed(self, frame):
        self.video_widget.videoSink().setVideoFrame(frame)
    
    @Slot(bool)
    def _observe_is_active_changed(self, val:bool):
        self._set_active(val)

    def _set_active(self, val:bool):
        msg = '' if val else 'Видео не доступно'
        self._set_msg_if_any(msg)
        
    @Slot()
    def _observe_paused(self):
        self._set_paused(True)

    @Slot()
    def _observe_played(self):
        self._set_paused(False)
    
    @Slot(bool)
    def _observe_is_paused_changed(self, val:bool):
        self._set_paused(val)
    
    def _set_paused(self, val:bool):
        msg = 'Видео приостановлено' if val else ''
        self._set_msg_if_any(msg)

    def _set_msg_if_any(self, msg):
        if msg:
            self.msg_label.setText(msg)
            # self.msg_label.setVisible()
            self.stacked_layout.setCurrentWidget(self.msg_label)
        else:
            self.msg_label.setText('')
            # self.msg_label.hide()
            self.stacked_layout.setCurrentIndex(0)

    def setup_ui(self):
        self.video_widget = QVideoWidget()
        self.video_widget.resize(QSize(300, 300))
        self.video_widget.setMaximumHeight(500)
        self.msg_label = QLabel()
        self.msg_label2 = QLabel()
        self.msg_label.setStyleSheet('background-color: rgba(255, 0, 0, 128); color: white;')

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.video_widget)
        self.stacked_layout.addWidget(self.msg_label2)
        self.stacked_layout.setCurrentIndex(0)
        self.setLayout(self.stacked_layout)
        


