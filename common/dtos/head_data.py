from datetime import datetime
from enum import Enum
from pydantic import Field, TypeAdapter, model_validator

from common.dtos.utils import PersonId

try:
    from .utils import FACE_KEYPOINTS_SHAPE, BaseConfig, FaceKeypoints, Quat, Vec3D
except:
    from utils import FACE_KEYPOINTS_SHAPE, BaseConfig, FaceKeypoints, Quat, Vec3D #type:ignore
from pydantic.dataclasses import dataclass
from PySide6.QtGui import QQuaternion, QVector3D


@dataclass(frozen=True, config=BaseConfig)
class EyeTransform:
    position: Vec3D
    rotation: Quat

@dataclass(frozen=True, config=BaseConfig)
class EyesTransforms:
    left_eye_transform:EyeTransform
    right_eye_transform:EyeTransform

@dataclass(frozen=True, config=BaseConfig)
class HeadProps:
    position: Vec3D
    rotation: Quat
    keypoints: FaceKeypoints

@dataclass(frozen=True, config=BaseConfig)
class HeadData:
    class ViewOrigin(Enum):
        NOT_VISIBLE='no_view'
        FACE='face'
        LEFT_EYE='left_eye'
        RIGHT_EYE='right_eye'

    timestamp:datetime = Field(default_factory=datetime.now)
    view_origin:ViewOrigin=ViewOrigin.NOT_VISIBLE
    head_props:HeadProps|None = None
    eyes_transforms:EyesTransforms|None = None

    @model_validator(mode='after') # type: ignore
    def validate_visibility_flag(self) -> 'HeadData':
        if self.view_origin != HeadData.ViewOrigin.NOT_VISIBLE:
            if self.head_props is None:
                raise ValueError('head_props should not be None when head is visible')
            if self.eyes_transforms is None:
                raise ValueError('eyes_transforms should not be None when head is visible')
        else:
            if self.head_props is not None:
                raise ValueError('head_props can not be not None when head is not visible')
            if self.eyes_transforms is not None:
                raise ValueError('eyes_transforms can not be not None when head is not visible')
            
        return self

@dataclass(frozen=True, config=BaseConfig)
class PersonHeadData:
    person_id:PersonId
    head_data:HeadData

HeadDataAdapter = TypeAdapter(HeadData)
PersonHeadDataAdapter = TypeAdapter(PersonHeadData)


if __name__ == '__main__':
    import numpy as np
    
    keypoints = np.random.normal(size=FACE_KEYPOINTS_SHAPE)
    head_props = HeadProps(position=QVector3D(1, 2, 3), rotation=QQuaternion(1, 0, 0, 0), keypoints=keypoints)
    left_eye = EyeTransform(QVector3D(0, 0.05, -0.02), QQuaternion())
    right_eye = EyeTransform(QVector3D(0, 0.05, 0.02), QQuaternion())
    eyes = EyesTransforms(left_eye, right_eye)
    head_data_visible = HeadData(view_origin=HeadData.ViewOrigin.FACE, head_props=head_props, eyes_transforms=eyes)
    head_data_not_visible = HeadData()

    print(f'{head_data_visible=}')
    print(f'{head_data_not_visible=}')

    head_data_adapter = TypeAdapter(HeadData)
    print(f'{head_data_adapter.dump_python(head_data_visible)=}')

    try:
        # invalid HeadData creation
        HeadData(view_origin=HeadData.ViewOrigin.FACE)
    except Exception as e:
        print(e)