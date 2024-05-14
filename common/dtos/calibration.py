from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

from common.dtos.head_data import HeadProps
from common.dtos.utils import BaseConfig, Vec3D


@dataclass(frozen=True, config=BaseConfig)
class CallibrationRecord:
    callibration_point_position:Vec3D
    head_props:HeadProps

CallibrationRecordsListAdapter = TypeAdapter(list[CallibrationRecord])