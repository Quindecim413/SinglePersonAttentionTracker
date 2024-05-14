from __future__ import annotations
from datetime import datetime
from typing import cast
from pydantic import TypeAdapter, ValidationInfo, field_validator
from pydantic.dataclasses import dataclass
from common.dtos.descriptions import AttentionRuleDescription, PersonDescription, SceneObjDescription
from common.dtos.head_data import HeadData
from common.dtos.hits import PerformedRayCastResult, AggregatedHit
from common.dtos.utils import BaseConfig


@dataclass(frozen=True, config=BaseConfig)
class PersonState(PersonDescription):
    head_data:HeadData
    last_cast_result:PerformedRayCastResult|None


@dataclass(frozen=True, config=BaseConfig)
class SceneObjState(SceneObjDescription):
    aggregated_hits:list[AggregatedHit]


@dataclass(frozen=True, config=BaseConfig)
class AttentionRuleState(AttentionRuleDescription):
    last_refresh_timestamp:datetime


def _extract_scene(validation_info:ValidationInfo):
    from common.domain.interfaces import AttentionScene
    context = cast(dict, validation_info.context or {})
    scene = cast(AttentionScene|None, context.get('scene'))
    if scene is None:
        raise ValueError(f'scene of {AttentionScene.__name__} should be provided in context')
    return scene


@dataclass(frozen=True, config=BaseConfig)
class AttentionSceneState:
    scene_objs:list[SceneObjState]
    persons:list[PersonState]
    rules:list[AttentionRuleState]

    @field_validator('scene_objs', mode='after')
    @classmethod
    def _validate_scene_objs_in_scene(cls, v:list[SceneObjState], validation_info:ValidationInfo):
        scene = _extract_scene(validation_info)

        scene_objs_by_id = scene.scene_objs_by_id()
        for scene_obj in v:
            if scene_obj.id not in scene_objs_by_id:
                raise ValueError('scene_objs do not match with scene')
        
        if len(scene_objs_by_id)!= len(v):
            raise ValueError('scene_objs do not match with scene')
        
        return v
    
    @field_validator('persons', mode='after')
    @classmethod
    def _validate_persons_in_scene(cls, v:list[PersonState], validation_info:ValidationInfo):
        scene = _extract_scene(validation_info)

        persons_by_is = scene.persons_by_id()
        for person in v:
            if person.id not in persons_by_is:
                raise ValueError('persons do not match with scene')
        
        if len(persons_by_is)!= len(v):
            raise ValueError('persons do not match with scene')
        
        return v
    
    @field_validator('rules', mode='after')
    @classmethod
    def _validate_rules_in_scene(cls, v:list[AttentionRuleState], validation_info:ValidationInfo):
        scene = _extract_scene(validation_info)

        rules_by_id = scene.attention_rules_by_id()
        for rule in v:
            if rule.id not in rules_by_id:
                raise ValueError('rules do not match with scene')
        
        if len(rules_by_id)!= len(v):
            raise ValueError('rules do not match with scene')
        
        return v


AttentionSceneStateAdapter = TypeAdapter(AttentionSceneState)
