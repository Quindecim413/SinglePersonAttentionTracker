from datetime import timedelta
from typing import TypeAlias
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

from common.dtos.utils import AttentionRuleId, BaseConfig, Color, PersonId, Quat, SceneObjId, Vec3D


@dataclass(frozen=True, config=BaseConfig)
class PersonDescription:
    id: PersonId
    name:str
    head_color:Color
    camera_position:Vec3D
    camera_rotation:Quat


# @dataclass_json
@dataclass(frozen=True, config=BaseConfig)
class SceneObjDescription:
    id:SceneObjId
    name:str
    keep_attention_timedelta:timedelta


@dataclass(frozen=True, config=BaseConfig)
class AttentionRuleDescription:
    id:AttentionRuleId
    name:str
    without_attention_timedelta:timedelta
    person_ids:list[PersonId]
    scene_obj_ids:list[SceneObjId]


@dataclass(frozen=True, config=BaseConfig)
class AttentionSceneDescription:
    scene_objs:list[SceneObjDescription]
    persons:list[PersonDescription]
    rules:list[AttentionRuleDescription]



PersonDescriptionAdapter = TypeAdapter(PersonDescription)
SceneObjDescriptionAdapter = TypeAdapter(SceneObjDescription)
AttentionRuleDescriptionAdapter = TypeAdapter(AttentionRuleDescription)
AttentionSceneDescriptionAdapter = TypeAdapter(AttentionSceneDescription)