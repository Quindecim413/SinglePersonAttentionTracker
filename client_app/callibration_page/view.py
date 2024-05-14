from abc import abstractmethod
from pathlib import Path
from typing import Any, Protocol
from PySide6.QtCore import Qt, QObject, Slot, Signal
from PySide6.QtWidgets import QWidget, QScrollArea, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QFileDialog
from PySide6.QtGui import QIcon, QImage

from common.collections.callibration import CallibrationRecordItem
from common.dtos.calibration import CallibrationRecord
from common.services.gaze.callibration import PersonGazeCallibrationService
from common.services.scene.scene_3d import AttentionScene3DService
from common.widgets.options import ItemView, ItemViewFactory, ItemsCollectionView, SelectItemsContainer
from .main_ui import Ui_page_callibration


class CallibrationRecordWidgetFactory(Protocol):
    @abstractmethod
    def __call__(self, record:CallibrationRecord) -> QWidget:
        ...


class CallibrationPageVM(QObject):
    can_finish_callibration_changed = Signal(bool)
    records_aggregation_progress_changed = Signal(int)

    running_callibration_changed = Signal(bool)
    computing_callibration_changed = Signal(bool)

    def __init__(self, 
                 scene_3d_service:AttentionScene3DService,
                 gaze_callibration_service:PersonGazeCallibrationService) -> None:
        super().__init__()
        self._scene3d = scene_3d_service
        self._scene3d.callibration_point_enabled_changed.connect(self._observe_callibration_point_enabled_changed)
        self._gaze_callibration_service = gaze_callibration_service
        self._gaze_callibration_service.callibration_started.connect(self._observe_callibration_started)
        self._gaze_callibration_service.callibration_failed.connect(self._observe_callibration_failed)
        self._gaze_callibration_service.callibration_ready.connect(self._observe_callibration_ready)
        self._gaze_callibration_service.callibration_records_collection().items_changed.connect(self._callibration_records_collection_items_changed)

        self._cached_can_finish_callibration = self.can_finish_callibration()
        self._running_callibration = self._scene3d.callibration_point_enabled()

    def running_callibration(self):
        return self._running_callibration
    
    def __set_running_callibration(self, val:bool):
        if self._running_callibration != val:
            self._running_callibration = val
            self.running_callibration_changed.emit(val)

    def can_finish_callibration(self) -> bool:
        return self._gaze_callibration_service.is_callibration_points_aggregated()
    
    def _try_update_can_finish_callibration(self):
        new_val = self.can_finish_callibration()
        if self._cached_can_finish_callibration != new_val:
            self._cached_can_finish_callibration = new_val
            self.can_finish_callibration_changed.emit(new_val)

    @Slot()
    def _callibration_records_collection_items_changed(self):
        self._gaze_callibration_service.callibration_records_collection()
        self._try_update_can_finish_callibration()
        
        self.__set_running_callibration(self._scene3d.callibration_point_enabled())
        self.records_aggregation_progress_changed.emit(self.records_aggregation_progress())

    def callibration_records_collection(self):
        return self._gaze_callibration_service.callibration_records_collection()
    
    def start_callibration(self):
        self.__set_running_callibration(True)
        self._gaze_callibration_service.reset_callibration()
        self._scene3d.enable_callibration_point(True)

    def stop_callibration(self):
        self.__set_running_callibration(False)
        self._gaze_callibration_service.reset_callibration()
        self._scene3d.enable_callibration_point(False)

    def finish_callibration(self):
        self.__set_running_callibration(False)
        if self._gaze_callibration_service.is_callibration_points_aggregated():
            self._gaze_callibration_service.callibrate()
            self._scene3d.enable_callibration_point(False)

    def add_callibration_record(self):
        self._gaze_callibration_service.capture_callibration_point()

    def computing_callibration(self) -> bool:
        return self._gaze_callibration_service.is_callibrating()

    def records_aggregation_progress(self) -> int:
        return len(self._gaze_callibration_service.callibration_records_collection())

    @Slot(bool)
    def _observe_callibration_point_enabled_changed(self, is_enabled):
        # self.
        pass
    
    def export_data(self, path:Path):
        self._gaze_callibration_service.export_points(path)

    @Slot()
    def _observe_callibration_started(self):
        self.computing_callibration_changed.emit(self._gaze_callibration_service.is_callibrating())

    @Slot()
    def _observe_callibration_failed(self):
        self.computing_callibration_changed.emit(self._gaze_callibration_service.is_callibrating())

    @Slot()
    def _observe_callibration_ready(self):
        self.computing_callibration_changed.emit(self._gaze_callibration_service.is_callibrating())


class CallibrationRecordItemView(ItemView[CallibrationRecordItem]):
    def __init__(self, 
                 item: CallibrationRecordItem, 
                 content:QWidget) -> None:
        super().__init__(item)

        remove_btn = QPushButton()
        remove_btn.setIcon(QIcon(str(Path(__file__).parent / 'src/trash.png')))
        remove_btn.clicked.connect(self._remove_btn_clicked)
        remove_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        hbox = QHBoxLayout()
        hbox.addWidget(content)
        hbox.addWidget(remove_btn)
        w = QWidget()
        w.setLayout(hbox)
        self.set_content(w)

    @Slot()
    def _remove_btn_clicked(self):
        self.item().remove_item()


class CallibrationRecordItemViewFactory(ItemViewFactory[CallibrationRecordItem]):
    def __init__(self, preview_widget_factory:CallibrationRecordWidgetFactory) -> None:
        super().__init__()
        self._preview_widget_factory = preview_widget_factory

    def __call__(self, item: CallibrationRecordItem) -> ItemView[CallibrationRecordItem]:
        return CallibrationRecordItemView(item, self._preview_widget_factory(item.record()))


class CallibrationPage(QWidget, Ui_page_callibration):
    def __init__(self, 
                 vm:CallibrationPageVM,
                 callibration_record_preview_widget_factory:CallibrationRecordWidgetFactory) -> None:
        super().__init__()
        self.vm = vm

        self.setupUi(self)

        self.vm.can_finish_callibration_changed.connect(self._observe_can_finish_callibration)
        self.vm.records_aggregation_progress_changed.connect(self._observe_aggregation_progress_changed)
        self.vm.computing_callibration_changed.connect(self._observe_computing_callibration_changed)
        self.vm.running_callibration_changed.connect(self._observe_running_callibration_changed)

        callibration_points_observe_widget = ItemsCollectionView(self.vm.callibration_records_collection(),
                                                                 CallibrationRecordItemViewFactory(callibration_record_preview_widget_factory))
        self.callibration_points_content.layout().addWidget(callibration_points_observe_widget)
        self.start_callibration_btn.clicked.connect(self._start_callibration_btn_clicked)
        self.stop_callibration_btn.clicked.connect(self._stop_callibration_btn_clicked)
        self.finish_callibration_btn.clicked.connect(self._finish_callibration_btn_clicked)
        self.add_callibration_point_btn.clicked.connect(self._add_callibration_point_clicked)
        self.export_data_btn.clicked.connect(self._export_callibration_clicked)

        self.export_data_btn.setVisible(False)
        
        self._set_running_callibration(self.vm.running_callibration())
        self._set_can_finish_callibration(self.vm.can_finish_callibration())
        self._set_aggregation_progress(self.vm.records_aggregation_progress())
        self._set_computing_callibration(self.vm.computing_callibration())

    @Slot()
    def _export_callibration_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Укажите файл для сохранения данных калибровки",
            "",  # Start directory
            "Json Files (*.json);;All Files (*)",
        )

        if not file_name:
            return
        if not file_name.endswith('.json'):
            file_name += '.json'
        self.vm.export_data(Path(file_name))

    @Slot()
    def _start_callibration_btn_clicked(self):
        self.vm.start_callibration()

    @Slot()
    def _stop_callibration_btn_clicked(self):
        self.vm.stop_callibration()

    @Slot()
    def _finish_callibration_btn_clicked(self):
        self.vm.finish_callibration()

    @Slot(bool)
    def _observe_running_callibration_changed(self, val:bool):
        self._set_running_callibration(val)

    def _set_running_callibration(self, val:bool):
        self.start_callibration_btn.setEnabled(not val)
        self.start_callibration_btn.setVisible(not val)

        self.stop_callibration_btn.setEnabled(val)
        self.stop_callibration_btn.setVisible(val)

        self.add_callibration_point_btn.setEnabled(val)

    @Slot()
    def _add_callibration_point_clicked(self):
        self.vm.add_callibration_record()

    @Slot(bool)
    def _observe_can_finish_callibration(self, val:bool):
        self._set_can_finish_callibration(val)

    def _set_can_finish_callibration(self, val:bool):
        self.finish_callibration_btn.setEnabled(val)
        # self.finish_callibration_btn.setVisible(val)

    @Slot(int)
    def _observe_aggregation_progress_changed(self, num_aggregated:int):
        self._set_aggregation_progress(num_aggregated)

    def _set_aggregation_progress(self, num_aggregated:int):
        self.callibration_progress_bar.setValue(num_aggregated)
    
    @Slot(bool)
    def _observe_computing_callibration_changed(self, val:bool):
        self._set_computing_callibration(val)

    def _set_computing_callibration(self, val:bool):
        self.setEnabled(not val)
