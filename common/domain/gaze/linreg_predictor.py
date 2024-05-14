from abc import abstractmethod
from typing import cast
from PySide6.QtGui import QVector3D, QQuaternion
from common.domain.gaze.eyes_direction_predictor import CallibrationRecord, EyeDirectionPredictor, HeadProps, EyesDirectionEstimator
from common.dtos.head_data import EyeTransform, EyesTransforms, HeadData
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def get_point_in_head_local(point:QVector3D, head_props:HeadProps) -> QVector3D:
    inverse_rotation = head_props.rotation.inverted()
    inverse_translation = -head_props.position
    callibration_point_head_local = inverse_rotation.rotatedVector(point) + inverse_translation
    return callibration_point_head_local



class LinRegEyeDirectionPredictor(EyeDirectionPredictor):
    def __init__(self, left_eye=True) -> None:
        super().__init__(left_eye)

        scaler = StandardScaler()
        model = LinearRegression()
        self._model_pipeline = make_pipeline(scaler, model)

    def fit(self, records:list[CallibrationRecord]):
        look_dir_local = [get_point_in_head_local(rec.callibration_point_position, rec.head_props).normalized() for rec in records]
        look_dir_local_np = np.array(list(map(lambda el: (el.x(), el.y(), el.z()), look_dir_local)), dtype=float)

        xs = np.array([self._make_x(rec.head_props) for rec in records], dtype=float)
        self._model_pipeline.fit(xs, look_dir_local_np)
        return

    def _make_x(self, head_props:HeadProps) -> np.ndarray:
        iris_pos = self.get_iris_position(head_props)
        iris_pos_local = get_point_in_head_local(QVector3D(*iris_pos), head_props)
        head_rotation_eulers = head_props.rotation.getEulerAngles()


    # @staticmethod
    def _approximate_eye_center(self, head_props:HeadProps):
        return QVector3D(*self.get_iris_position(head_props)) - QVector3D(0, 0, -0.012)
    
    def predict(self, head_props:HeadProps) -> EyeTransform:
        """computes translation and rotation angles of eye based on raw_iris_position"""
        eye_tr = EyeTransform(
            position=self._approximate_eye_center(head_props),
            rotation=QQuaternion()
        )
        return eye_tr