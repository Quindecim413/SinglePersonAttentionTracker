import base64
from enum import Enum
from typing import Any, TypeAlias, cast
from typing_extensions import Annotated
from pydantic import AfterValidator, BaseModel, BeforeValidator, TypeAdapter, field_validator, field_serializer, WrapSerializer, PlainSerializer, model_validator
from PySide6.QtGui import QVector3D, QQuaternion, QColor
import numpy as np
from pydantic.dataclasses import dataclass

FACE_KEYPOINTS_SHAPE = (478, 3)


PersonId:TypeAlias = int
SceneObjId:TypeAlias = str
AttentionRuleId:TypeAlias = int

def maybe_list_to_vec3(v:Any):
    if isinstance(v, QVector3D):
        return v
    if isinstance(v, (list, tuple)) and len(v) == 3:
        return QVector3D(*v)
    raise ValueError('Invalid values for QVector3D')

def maybe_list_to_color(v:Any):
    if isinstance(v, QColor):
        return v
    if isinstance(v, (list, tuple)) and (len(v) == 3 or len(v) == 4):
        rgba_codes = list(map(int, v))
        return QColor(*rgba_codes)
    raise ValueError('Invalid values for QColor')

def maybe_eulers_to_quat(v:Any):
    if isinstance(v, QQuaternion):
        return v
    if isinstance(v, (list, tuple)) and len(v) == 3:
        return QQuaternion.fromEulerAngles(v[0], v[1], v[2])
    raise ValueError('Invalid values for QQuaternion')

def vec3_serializer(v:QVector3D):
    if not isinstance(v, QVector3D):
        raise TypeError()
    return (v.x(), v.y(), v.z())

def color_serializer(c:QColor):
    if not isinstance(c, QColor):
        raise TypeError()
    return cast(tuple[int, int, int, int], c.toTuple())

def quat2eulers_serializer(q:QQuaternion):
    if not isinstance(q, QQuaternion):
        raise TypeError()
    
    return cast(tuple[float, float, float], q.toEulerAngles().toTuple())

def maybe_keypoints(keypoints:Any):
    if isinstance(keypoints, np.ndarray):
        if not keypoints.shape == FACE_KEYPOINTS_SHAPE:
            raise ValueError(f'face keypoints should have shape {FACE_KEYPOINTS_SHAPE}')
        keypoints = keypoints.astype(float)
        return keypoints
    return keypoints_decode(keypoints)
    
def keypoints_decode(keypoints_encoded:str):
    if not isinstance(keypoints_encoded, str):
        raise TypeError()
    keypoints_bytes = base64.b64decode(keypoints_encoded)
    keypoints = np.frombuffer(keypoints_bytes, dtype=np.float32).reshape(FACE_KEYPOINTS_SHAPE)
    if not keypoints.shape == FACE_KEYPOINTS_SHAPE:
        raise ValueError(f'face keypoints should have shape {FACE_KEYPOINTS_SHAPE}')
    return keypoints
    
    
def keypoints_encode(keypoints:np.ndarray):
    if not isinstance(keypoints, np.ndarray):
        raise TypeError()
    if not keypoints.shape == FACE_KEYPOINTS_SHAPE:
        raise ValueError(f'face keypoints should have shape {FACE_KEYPOINTS_SHAPE}')
    serialized_keypoints = keypoints.astype(np.float32).tobytes()

    encoded_keypoints = base64.b64encode(serialized_keypoints).decode('utf-8')

    # original_size = len(serialized_keypoints)
    # compressed_size = len(encoded_keypoints)

    # # Calculate the compression ratioc
    # compression_ratio = original_size / compressed_size
    # print(f'{original_size=} {compressed_size=} {compression_ratio=}')

    return encoded_keypoints


Vec3D = Annotated[QVector3D, BeforeValidator(maybe_list_to_vec3), PlainSerializer(vec3_serializer, when_used='json')]
Quat = Annotated[QQuaternion, BeforeValidator(maybe_eulers_to_quat), PlainSerializer(quat2eulers_serializer, when_used='json')]
Color = Annotated[QColor, BeforeValidator(maybe_list_to_color), PlainSerializer(color_serializer, when_used='json')]
FaceKeypoints = Annotated[np.ndarray, BeforeValidator(maybe_keypoints), PlainSerializer(keypoints_encode, when_used='json', return_type=str)]

class BaseConfig:
    arbitrary_types_allowed=True


    