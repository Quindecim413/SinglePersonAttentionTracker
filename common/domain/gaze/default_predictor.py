from abc import abstractmethod
from PySide6.QtGui import QVector3D, QQuaternion
from common.domain.gaze.eyes_direction_predictor import CallibrationRecord, EyeDirectionPredictor, HeadProps, EyesDirectionEstimator
from common.dtos.head_data import EyeTransform, EyesTransforms





class DefaultEyeDirectionPredictor(EyeDirectionPredictor):
    def fit(self, records:list[CallibrationRecord]):
        return
    
    def predict(self, head_props:HeadProps) -> EyeTransform:
        """computes translation and rotation angles of eye based on raw_iris_position"""
        eye_tr = EyeTransform(
            position=QVector3D(*self.get_iris_position(head_props)) - QVector3D(0, 0, -0.012),#cast(tuple[float, float, float], raw_iris_position - rotate_vector(euler2quat(*head_rotation_xyz)))
            rotation=QQuaternion()
        )
        return eye_tr