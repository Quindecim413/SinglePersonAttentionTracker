from common.domain.gaze.default_predictor import DefaultEyeDirectionPredictor
from common.domain.gaze.eyes_direction_predictor import EyesCallibrator, EyesDirectionEstimator
from common.dtos.calibration import CallibrationRecord



class DefaultEyesCallibrator(EyesCallibrator):
    def callibrate(self, records: list[CallibrationRecord], using_eyes:EyesCallibrator.UsingEyes) -> EyesDirectionEstimator:
        estimator = EyesDirectionEstimator(DefaultEyeDirectionPredictor(), DefaultEyeDirectionPredictor(left_eye=False))
        estimator.fit(records)
        return estimator
