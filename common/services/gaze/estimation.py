from pathlib import Path
from typing import Protocol
from PySide6.QtCore import QObject, Slot, Signal
from common.domain.gaze.eyes_direction_predictor import EyesDirectionEstimator, FileCorrupted
from common.domain.gaze.head_data_estimator import HeadDataEstimator
from common.domain.interfaces import Person
from common.dtos.head_data import HeadData
from common.services.face_scanning.face_scanner import FaceScanResult, FaceScannerService
from common.services.gaze.callibration import PersonGazeCallibrationService


class HeadDataEstimatorFactory(Protocol):
    def create_default(self) -> HeadDataEstimator:
        ...
    
    def create(self, eyes_direction_estimator:EyesDirectionEstimator) -> HeadDataEstimator:
        ...


class PersonGazeEstimationService(QObject):
    predictor_loading_complete = Signal()
    estimator_loading_failed = Signal(str)
    estimator_changed = Signal()
    person_changed = Signal()
    def __init__(self, 
                 callibration_service:PersonGazeCallibrationService,
                 face_scanner:FaceScannerService,
                 head_data_estimator_factory:HeadDataEstimatorFactory):
        super().__init__()
        self._head_data_estimator_factory = head_data_estimator_factory
        self._face_scanner = face_scanner
        self._person:Person|None = None
        self._head_data_estimator:HeadDataEstimator = self._head_data_estimator_factory.create_default()
        self._set_eyes_direction_estimator(None)
        
        self._callibration_service = callibration_service
        self._callibration_service.callibration_ready.connect(self._observe_callibration_ready)
        self._face_scanner.face_scanned.connect(self._observe_face_scanned)

    def _set_eyes_direction_estimator(self, estimator:EyesDirectionEstimator|None):
        if not estimator:
            self._head_data_estimator.disconnect(self)
            self._head_data_estimator = self._head_data_estimator_factory.create_default()
        else:
            self._head_data_estimator = self._head_data_estimator_factory.create(estimator)

        self.estimator_changed.emit()

    def person(self):
        return self._person

    def set_person(self, person:Person|None):
        if self._person != person:
            self.person_changed.emit()
        self._person = person
        
    def _observe_callibration_ready(self, eyes_direction_estimator:EyesDirectionEstimator):
        self._set_eyes_direction_estimator(eyes_direction_estimator)

    def head_data_estimator(self) -> HeadDataEstimator:
        return self._head_data_estimator
        
    @Slot(FaceScanResult)
    def _observe_face_scanned(self, face_scan_results:FaceScanResult):
        if (person:=self._person) and (estimator:=self._head_data_estimator):
            head_data = estimator.predict(face_scan_results)
            person.set_head_data(head_data)
    
    def load_estimator_from_path(self, path:Path):
        try:
            eyes_direction_estimator = EyesDirectionEstimator.load_from_file(path)
        except FileNotFoundError as err:
            self.estimator_loading_failed.emit(f'Файл {path} не найден')
        except IOError as err:
            self.estimator_loading_failed.emit(f"Не удалось загрузить файл {path}")
        except FileCorrupted as err:
            self.estimator_loading_failed.emit('Возникла ошибка при чтении файла:\n'+str(err))
        self.predictor_loading_complete.emit()
        self._set_eyes_direction_estimator(eyes_direction_estimator)
