from PySide6.QtCore import Qt, Slot, QObject, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtMultimedia import QMediaCaptureSession, QVideoSink, QVideoFrame, QCameraDevice, QCamera, QMediaDevices
from PySide6.QtMultimediaWidgets import QVideoWidget

from common.utils import clear_layout
from ..services.video.camera import CameraService
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QButtonGroup, QGridLayout, QRadioButton, QSplitter, QGroupBox, QPushButton, QScrollArea, QSizePolicy
from pathlib import Path


class CameraConfigureVM(QObject):
    camera_device_names_changed = Signal(list) #list[str]
    is_mirrored_changed = Signal(bool)

    def __init__(self, camera_service:CameraService) -> None:
        super().__init__()
        self._camera_service = camera_service
        self._camera_service.play()
        self._media_devices = QMediaDevices()
        self._media_devices.videoInputsChanged.connect(self._observe_video_devices_changed)
        self._camera_service.is_mirrored_changed.connect(self._observe_is_mirrored_changed)

    @Slot(bool)
    def _observe_is_mirrored_changed(self, is_mirrored:bool):
        self._set_is_mirrored(is_mirrored)

    def _set_is_mirrored(self, is_mirrored:bool):
        self.is_mirrored_changed.emit(is_mirrored)

    def is_mirrored(self):
        return self._camera_service.is_mirrored()
    
    @Slot()
    def rotate_cw(self):
        self._camera_service.rotate_clockwise()
    
    @Slot()
    def rotate_ccw(self):
        self._camera_service.rotate_counter_clockwise()

    @Slot()
    def reflect(self):
        self._camera_service.set_mirrored(not self._camera_service.is_mirrored())

    @Slot()
    def restore_default_transform(self):
        self._camera_service.set_rotation_angle(QVideoFrame.RotationAngle.Rotation0)
        self._camera_service.set_mirrored(False)

    @Slot()
    def _observe_video_devices_changed(self):
        self.set_active_camera_devices(self._media_devices.videoInputs())

    def camera_device_names(self):
        return [dev.description() for dev in self._media_devices.videoInputs()
                    if not dev.isNull()]

    def set_active_camera_devices(self, devices:list[QCameraDevice]):
        names = [dev.description() for dev in devices if not dev.isNull()]
        self.camera_device_names_changed.emit(names)

    def is_camera_device_selected(self, name:str) -> bool:
        device = self._camera_service.device()
        if not device:
            return False
        
        return device.description() == name
    
    @Slot(str)
    def select_camera_device(self, name:str):
        device = next(filter(lambda dev: dev.description() == name, self._media_devices.videoInputs()), None)
        if device:
            self._camera_service.set_device(device)
        

class CameraConfigureWidget(QWidget):
    def __init__(self, vm:CameraConfigureVM,
                 camera_preview_widget:QWidget) -> None:
        super().__init__()
        self.vm = vm
        self.camera_preview_widget = camera_preview_widget
        self.setup_ui()
        
        self.bg = QButtonGroup()
        self.bg.idClicked.connect(self._handle_id_clicked)
        self.id2cam_name:dict[int, str] = {}

        self.vm.camera_device_names_changed.connect(self._observe_camera_device_names_changed)
        self.set_video_devices_options(self.vm.camera_device_names())

        self.vm.is_mirrored_changed.connect(self._observe_is_mirrored_changed)
        self._rotate_cw_btn.clicked.connect(self.vm.rotate_cw)
        self._rotate_ccw_btn.clicked.connect(self.vm.rotate_ccw)
        self._reflect_btn.clicked.connect(self.vm.reflect)
        self._restore_transform_btn.clicked.connect(self.vm.restore_default_transform)
        self._set_is_mirrored(self.vm.is_mirrored())
        
    @Slot(bool)
    def _observe_is_mirrored_changed(self, is_mirrored:bool):
        self._set_is_mirrored(is_mirrored)

    def _set_is_mirrored(self, is_mirrored:bool):
        if self._reflect_btn.isChecked()!= is_mirrored:
            self._reflect_btn.setChecked(is_mirrored)
    
    @Slot(list)
    def _observe_camera_device_names_changed(self, names:list[str]):
        self.set_video_devices_options(names)

    def set_video_devices_options(self, devices:list[str]):
        btns = self.bg.buttons()
        for btn in btns:
            self.bg.removeButton(btn)
        
        vbox = self.cam_devices_box.layout()
        clear_layout(vbox)
        self.id2cam_name.clear()

        for ind, device in enumerate(devices):
            btn = QRadioButton(device)
            if self.vm.is_camera_device_selected(device):
                btn.setChecked(True)
            self.bg.addButton(btn)
            self.bg.setId(btn, ind)
            self.id2cam_name[ind] = device

            vbox.addWidget(btn)
    
    @Slot(int)
    def _handle_id_clicked(self, id:int):
        self.vm.select_camera_device(self.id2cam_name[id])

    def setup_ui(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.camera_preview_widget.setMinimumWidth(200)
        self.camera_preview_widget.setMinimumHeight(200)
        self.camera_preview_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)

        content_widget = QWidget()
        content_vbox = QVBoxLayout()
        content_widget.setLayout(content_vbox)
        # content_vbox.addWidget(QLabel('Hellow content widget'))
        self.scroll_area.setWidget(content_widget)


        # Available devices
        self.cam_devices_box = QGroupBox()
        self.cam_devices_box.setTitle('Доступные камеры')
        
        self.cam_devices_box.setMinimumHeight(100)
        self.cam_devices_box.setLayout(QVBoxLayout())
        

        # Control buttons
        src_dir = Path(__file__).parent / 'src'

        self._rotate_cw_btn = QPushButton(QIcon(str(src_dir / 'cw-arrow.png')), '')
        self._rotate_ccw_btn = QPushButton(QIcon(str(src_dir / 'ccw-arrow.png')), '')
        self._reflect_btn = QPushButton(QIcon(str(src_dir / 'reflect.png')), '')
        self._reflect_btn.setCheckable(True)
        self._restore_transform_btn = QPushButton(QIcon(str(src_dir / 'restore.png')), '')

        controls_area = QWidget()
        # controls_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        vbox = QVBoxLayout()
        grid = QGridLayout()
        grid.addWidget(self._rotate_ccw_btn, 0, 0)
        grid.addWidget(self._rotate_cw_btn, 0, 1)
        grid.addWidget(self._reflect_btn, 1, 0)
        grid.addWidget(self._restore_transform_btn, 1, 1)
        info_lbl = QLabel('Трансформации изображения')
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        vbox.addWidget(info_lbl)
        vbox.addLayout(grid)
        vbox.addStretch(1)
        controls_area.setLayout(vbox)


        # setup
        
        main_vbox = QVBoxLayout()
        
        main_vbox.addWidget(controls_area)
        main_vbox.addWidget(self.camera_preview_widget)
        
        content_vbox.addWidget(self.cam_devices_box)
        content_vbox.addStretch(1)
        

        main_vbox.addWidget(self.scroll_area)
        main_vbox.addWidget(QLabel('HELLO LABEL'))
        self.setLayout(main_vbox)
        
        # self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)

        

    # def setup_ui(self):
    #     self.scroll_area = QScrollArea()
        


    #     self.splitter = QSplitter()
    #     self.splitter.setHandleWidth(10)
    #     self.splitter.setStyleSheet("""
    #         QSplitter::handle {
    #         margin: 1px 5px;
    #         border: 2px dashed;
    #         }

    #         QSplitterHandle:hover {}

    #         QSplitter::handle:horizontal:hover {
    #         background-color: #555;
    #         } 
    #     """)
    #     self.splitter.addWidget(self.camera_preview_widget)
    #     self.camera_preview_widget.setMinimumWidth(200)

    #     self.cam_devices_box = QGroupBox()
    #     self.cam_devices_box.setTitle('Доступные камеры')
        
    #     self.cam_devices_box.setMinimumHeight(100)
    #     self.cam_devices_box.setLayout(QVBoxLayout())
        
    #     src_dir = Path(__file__).parent / 'src'

    #     self._rotate_cw_btn = QPushButton(QIcon(str(src_dir / 'cw-arrow.png')), '')
    #     self._rotate_ccw_btn = QPushButton(QIcon(str(src_dir / 'ccw-arrow.png')), '')
    #     self._reflect_btn = QPushButton(QIcon(str(src_dir / 'reflect.png')), '')
    #     self._reflect_btn.setCheckable(True)
    #     self._restore_transform_btn = QPushButton(QIcon(str(src_dir / 'restore.png')), '')

    #     controls_area = QWidget()
    #     # controls_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
    #     vbox = QVBoxLayout()
    #     grid = QGridLayout()
    #     grid.addWidget(self._rotate_ccw_btn, 0, 0)
    #     grid.addWidget(self._rotate_cw_btn, 0, 1)
    #     grid.addWidget(self._reflect_btn, 1, 0)
    #     grid.addWidget(self._restore_transform_btn, 1, 1)
    #     info_lbl = QLabel('Трансформации изображения')
    #     info_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
    #     vbox.addWidget(info_lbl)
    #     vbox.addLayout(grid)
    #     vbox.addWidget(self.cam_devices_box)
    #     vbox.addStretch(1)
    #     controls_area.setLayout(vbox)
    #     self.splitter.addWidget(controls_area)

    #     vbox2 = QVBoxLayout()
    #     vbox2.addWidget(self.splitter)
    #     self.setLayout(vbox2)

    #     self.splitter.setCollapsible(0, False)
    #     self.splitter.setCollapsible(1, False)
        
    #     # self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)

        



