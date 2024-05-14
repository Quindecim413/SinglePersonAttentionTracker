from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from pickle import UnpicklingError, dump, load
from typing import Literal, Protocol, final, runtime_checkable
from numpy.typing import NDArray
import numpy as np
from PySide6.QtCore import QObject
from PySide6.QtGui import QVector3D, QQuaternion
from common.dtos.calibration import CallibrationRecord
from common.dtos.head_data import EyeTransform, EyesTransforms
from common.dtos.head_data import HeadProps


class FileCorrupted(Exception):
    def __init__(self, path:Path, reason_msg:str) -> None:
        super().__init__(f'File {path} could not be read. Reason :{reason_msg}')


LEFT_IRIS_IND  = 473
RIGHT_IRIS_IND = 468

class EyeDirectionPredictor:
    def __init__(self, left_eye=True) -> None:
        self._left_eye = left_eye
    
    def is_left_eye(self) -> bool:
        return self._left_eye

    def get_iris_position(self, head_props:HeadProps) -> NDArray[np.float32]:
        """Return arrays of 3 float32, representing coordinates of iris"""
        return head_props.keypoints[LEFT_IRIS_IND if self._left_eye else RIGHT_IRIS_IND]

    @abstractmethod
    def fit(self, records:list[CallibrationRecord]) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def predict(self, head_props:HeadProps) -> EyeTransform:
        raise NotImplementedError()


class FitNotDoneError(Exception):
    pass


@final
class EyesDirectionEstimator:
    def __init__(self,
                 left_eye_predictor:EyeDirectionPredictor,
                 right_eye_predictor:EyeDirectionPredictor,
                 ) -> None:
        self._left_eye_predictor = left_eye_predictor
        self._right_eye_predictor = right_eye_predictor
        self._fitted = False

    def fit(self, records:list[CallibrationRecord]) -> None:
        self._left_eye_predictor.fit(records)
        self._right_eye_predictor.fit(records)
        self._fitted = True
    
    def predict(self, head_props:HeadProps) -> EyesTransforms:
        if not self._fitted:
            raise FitNotDoneError()
        left_eye_tr = self._left_eye_predictor.predict(head_props)
        right_eye_tr = self._right_eye_predictor.predict(head_props)
        return EyesTransforms(left_eye_transform=left_eye_tr, right_eye_transform=right_eye_tr)
    
    def save_to_file(self, filepath:Path):
        with open(filepath, 'wb') as file:
            dump(self, file)
    
    @staticmethod
    def load_from_file(filepath:Path) -> 'EyesDirectionEstimator':
        with open(filepath, 'rb') as file:
            try:
                eyes_direction_predictor = load(file)
            except UnpicklingError as err:
                raise FileCorrupted(filepath, str(err))
        if not isinstance(eyes_direction_predictor, EyesDirectionEstimator):
            raise TypeError(f'{filepath} should contain {EyesDirectionEstimator.__class__}, found {type(eyes_direction_predictor).__name__}')

        return eyes_direction_predictor


class EyesCallibrator:
    class UsingEyes(Enum):
        BOTH = 0
        LEFT = 1
        RIGHT = 2
        NONE = 3

    @abstractmethod
    def callibrate(self, records:list[CallibrationRecord], using_eyes:UsingEyes) -> EyesDirectionEstimator:
        """Проведение непосредственной каллибровки"""
        ...
