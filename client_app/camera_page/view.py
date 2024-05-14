from pathlib import Path
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton, QLabel
from PySide6.QtGui import QIcon, QAction
from common.services.face_scanning.face_scanner import FaceScannerService
from common.widgets.camera_configure import CameraConfigureWidget


class CameraPage(QWidget):
    def __init__(self, 
                 camera_configure_widget:CameraConfigureWidget,
                 face_scanner:FaceScannerService) -> None:
        super().__init__()
        self._face_scanner = face_scanner
        self._camera_configure_widget = camera_configure_widget

        self._video_service = self._face_scanner.video_service()
        self._video_service.source_description_changed.emit(self._observe_source_description_changed)
        self._video_service.is_available_changed.connect(self._observe_video_source_is_available_changed)

        pause_btn_path = str(Path(__file__).parent / 'src/pause.png')
        play_btn_path = str(Path(__file__).parent / 'src/play.png')
        icon = QIcon()
        icon.addFile(play_btn_path, QSize(), QIcon.Mode.Normal, QIcon.State.On)
        icon.addFile(pause_btn_path, QSize(), QIcon.Mode.Active, QIcon.State.Off)
        
        self.controls_action = QAction(icon, 'Управление')
        self.controls_action.setCheckable(True)
        self.controls_action.setChecked(self._video_service.is_paused())
        self.controls_action.toggled.connect(self._play_controls_toggled)

        self._play_control_btn = QToolButton()
        self._play_control_btn.setDefaultAction(self.controls_action)
        self._description_lbl = QLabel(self._video_service.source_description())
        self._description_lbl.setWordWrap(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self._play_control_btn)
        hbox.addWidget(self._description_lbl)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self._camera_configure_widget)
        self.setLayout(vbox)

        self._set_video_source_is_available(self._video_service.is_available())

    @Slot(bool)
    def _observe_video_source_is_available_changed(self, is_available:bool):
        self._set_video_source_is_available(is_available)
    
    def _set_video_source_is_available(self, is_available:bool):
        self._play_control_btn.setEnabled(is_available)

    @Slot(str)
    def _observe_source_description_changed(self, description:str):
        self._description_lbl.setText(description)

    @Slot(bool)
    def _play_controls_toggled(self, active:bool):
        if active:
            self._video_service.play()
        else:
            self._video_service.pause()
