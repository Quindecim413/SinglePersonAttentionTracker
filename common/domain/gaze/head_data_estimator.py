from typing import cast
from PySide6.QtCore import QObject, Slot, Signal
from common.domain.gaze.eyes_direction_predictor import EyesDirectionEstimator
from common.domain.interfaces import Person
from common.dtos.head_data import HeadData, HeadProps
from common.services.face_scanning.face_scanner import FaceScanResult, FaceScannerService


vec3 = tuple[float, float, float]
class HeadDataEstimator(QObject):
    def __init__(self, 
                 eyes_direction_estimator:EyesDirectionEstimator,
                 parent=None) -> None:
        super().__init__()
        self._person:Person|None = None
        self._eyes_direction_estimator = eyes_direction_estimator

    def predict(self, scan_results: FaceScanResult) -> HeadData:
        if not scan_results.head_visible:
            head_data = HeadData()
        else:
            head_props = cast(HeadProps, scan_results.head_props)
            x, yaw, z = cast(vec3, head_props.rotation.toEulerAngles().toTuple()) # x: pitch, y: yaw, z: -roll
            # yaw = np.rad2deg(y)

            if -45 < yaw < 45:
                if yaw < 0:
                    view_origin = HeadData.ViewOrigin.RIGHT_EYE
                else:
                    view_origin = HeadData.ViewOrigin.LEFT_EYE
            else:
                view_origin = HeadData.ViewOrigin.FACE
            
            eyes_transforms = self._eyes_direction_estimator.predict(head_props)

            head_data = HeadData(head_props=head_props,
                                eyes_transforms=eyes_transforms,
                                view_origin=view_origin)

        return head_data
        # self.head_data_generated.emit(head_data)
