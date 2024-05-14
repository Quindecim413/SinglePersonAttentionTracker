from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Type, cast
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QVector3D, QQuaternion
from common.collections.callibration import CallibrationRecordsCollection
from common.domain.gaze.eyes_direction_predictor import EyesCallibrator, EyesDirectionEstimator
from common.domain.interfaces import Person
from common.dtos.calibration import CallibrationRecord, CallibrationRecordsListAdapter
from common.dtos.head_data import HeadProps
from common.services.face_scanning.face_scanner import FaceScannerService
from common.services.video.types import VideoService
import numpy as np
from typing import Protocol


class NotReadyToCallibrate(RuntimeError):
    def __init__(self, total_points:int, min_points:int) -> None:
        super().__init__(f'PersonGazeCallibrationService is not ready to callibrate. CallibrationRecords agregation progrees is {total_points}/{min_points}')
        self.total_points = total_points
        self.min_points = min_points



class PersonGazeCallibrationService(QObject):
    class UsingEyes(Enum):
        BOTH = 0
        LEFT = 1
        RIGHT = 2
        NONE = 3
    
    callibration_started = Signal()
    callibration_ready = Signal(EyesDirectionEstimator)
    callibration_failed = Signal(str) # reason
    callibration_points_aggregated = Signal()
    record_added = Signal(CallibrationRecord)
    records_cleared = Signal()
    using_eyes_changed = Signal(UsingEyes)
    target_point_changed = Signal(QVector3D)

    def __init__(self,
                 eyes_callibrator:EyesCallibrator,
                 face_scanner:FaceScannerService,
                 min_callibration_points:int=10,
                 ) -> None:
        super().__init__()
        self._min_callibration_points = min_callibration_points
        self._face_scanner = face_scanner
        self._records_collection = CallibrationRecordsCollection()
        self._eyes_callibrator = eyes_callibrator
        self._target_point = QVector3D()
        self._using_eyes = EyesCallibrator.UsingEyes.BOTH
        self._is_callibrating = False

    def callibration_records_collection(self):
        return self._records_collection

    def reset_callibration(self):
        self._records_collection.reset()
        self.records_cleared.emit()

    def set_using_eyes(self, using_eyes:EyesCallibrator.UsingEyes):
        if self._using_eyes != using_eyes:
            self._using_eyes = using_eyes
            self.using_eyes_changed.emit(using_eyes)

    def set_target_point(self, point:QVector3D):
        if not isinstance(point, QVector3D):
            raise TypeError(f'point should be instance of QVector3D, found {point} of type {type(point)}')
        if self._target_point != point:
            self._target_point = point
            self.target_point_changed.emit(point)
    
    def capture_callibration_point(self):
        if res:=self._face_scanner.last_scan_result():
            if res.head_visible:
                head_props = cast(HeadProps, res.head_props)
                record = CallibrationRecord(self._target_point,
                                            head_props)
                self._records_collection.add_record(record)
                self.record_added.emit(record)
                if self._min_callibration_points <= len(self._records_collection):
                    self.callibration_points_aggregated.emit()

    def is_callibration_points_aggregated(self):
        return self._min_callibration_points <= len(self._records_collection)

    def is_callibrating(self):
        return self._is_callibrating
    
    def export_points(self, path:Path):
        records = self._records_collection.records()
        with open(path, 'wb') as f:
            f.write(CallibrationRecordsListAdapter.dump_json(records))

    def callibrate(self):
        if not self.is_callibration_points_aggregated():
            raise NotReadyToCallibrate(len(self._records_collection), self._min_callibration_points)
        self.callibration_started.emit()
        self._is_callibrating = True
        try:
            eyes_direction_estimator = self._eyes_callibrator.callibrate(self._records_collection.records(), self._using_eyes)
            
            self._is_callibrating = False
            self.callibration_ready.emit(eyes_direction_estimator)
        except Exception as e:
            self._is_callibrating = False
            self.callibration_failed.emit(str(e))
        
