from __future__ import annotations
from datetime import timedelta, datetime
from typing import Any, Protocol
from abc import ABCMeta, abstractmethod, ABC
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QColor, QVector3D, QQuaternion

from common.domain.scene_timer import SceneUpdateTimer
from common.dtos.descriptions import AttentionSceneDescription
from common.dtos.head_data import HeadData
from common.dtos.hits import PerformedRayCastResult, AggregatedHit, SceneObjAttentionHits
from common.dtos.states import AttentionSceneState


class SceneElement(QObject):
    element_name_changed = Signal(str)
    
    removed_from_scene = Signal()

    is_selected_changed = Signal(bool)
    is_errored_changed = Signal(bool)
    is_tracking_changed = Signal(bool)

    has_selected_state_changed = Signal(bool)
    has_errored_state_changed = Signal(bool)
    has_tracking_state_changed = Signal(bool)

    @abstractmethod
    def element_id(self) -> Any:
        raise NotImplementedError()
    
    @abstractmethod
    def element_name(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def set_element_name(self, name:str):
        raise NotADirectoryError

    @abstractmethod
    def remove_from_scene(self):
        raise NotImplementedError()
    
    @abstractmethod
    def is_removed_from_scene(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def has_tracking_state(self) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def has_errored_state(self) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def has_selected_state(self) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def is_selected(self)-> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def set_selected(self, val:bool):
        raise NotImplementedError()
    
    @abstractmethod
    def is_errored(self) -> bool:
        raise  NotImplementedError()

    @abstractmethod
    def set_errored(self, val:bool):
        raise NotImplementedError()
    
    @abstractmethod
    def __contains__(self, other:'SceneElement'):
        raise NotImplementedError()
    
    @abstractmethod
    def scene(self) -> 'AttentionScene':
        raise NotImplementedError()


class SceneObj(SceneElement):
    added_to_rule = Signal(object)
    removed_from_rule = Signal(object)

    keep_attention_timedelta_changed = Signal(timedelta)

    registered_attention = Signal(SceneObjAttentionHits)
    aggregated_attention_hits_changed = Signal()
    aggregated_attention_hits_added = Signal(list[AggregatedHit])

    @abstractmethod
    def keep_attention_timedelta(self) -> timedelta:
        raise NotImplementedError()

    @abstractmethod
    def set_keep_attention_timedelta(self, tdelta:timedelta):
        raise NotImplementedError()
    
    @abstractmethod
    def register_attention(self, attention_hit:SceneObjAttentionHits) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def set_aggregated_hits(self, aggregated_hit:list[AggregatedHit])->None:
        raise NotImplementedError()
    
    @abstractmethod
    def rules(self) -> list['AttentionRule']:
        raise NotImplementedError()
    
    @abstractmethod
    def aggregated_hits(self) -> list[AggregatedHit]:
        raise NotImplementedError()


class Person(SceneElement):
    added_to_rule = Signal(object)
    removed_from_rule = Signal(object)

    head_color_changed = Signal(QColor) # 3 x int
    camera_position_changed = Signal(QVector3D) # 3 x float
    camera_rotation_changed = Signal(QQuaternion) # 3 x float

    performed_ray_cast_result_changed = Signal()

    head_data_changed = Signal(HeadData)

    @abstractmethod
    def head_color(self)->QColor:
        raise NotADirectoryError()
    
    @abstractmethod
    def set_head_color(self, color:QColor):
        raise NotImplementedError()
    
    @abstractmethod
    def camera_position(self) -> QVector3D:
        raise NotImplementedError()
    
    @abstractmethod
    def set_camera_position(self, position:QVector3D):
        raise NotImplementedError()
    
    @abstractmethod
    def camera_rotation(self) -> QQuaternion:
        raise NotImplementedError()
    
    @abstractmethod
    def set_camera_rotation(self, rotation:QQuaternion):
        raise NotImplementedError()
    
    @abstractmethod
    def set_head_data(self, data:HeadData):
        raise NotImplementedError()
    
    @abstractmethod
    def head_data(self) -> HeadData:
        raise NotImplementedError()
    
    @abstractmethod
    def set_performed_ray_cast_result(self, cast_result:PerformedRayCastResult):
        raise NotImplementedError()
    
    @abstractmethod
    def performed_ray_cast_result(self) -> PerformedRayCastResult|None:
        raise NotImplementedError()
    
    @abstractmethod
    def rules(self) -> list['AttentionRule']:
        raise NotImplementedError()


class AttentionRule(SceneElement):
    person_added = Signal(Person)
    person_removed = Signal(Person)
    scene_obj_added = Signal(SceneObj)
    scene_obj_removed = Signal(SceneObj)
    
    last_refresh_timestamp_changed = Signal(datetime)
    without_attention_timedelta_changed = Signal(timedelta)

    @abstractmethod
    def persons(self) -> list[Person]:
        raise NotImplementedError()
    
    @abstractmethod
    def scene_objs(self) -> list[SceneObj]:
        raise NotImplementedError()
    
    @abstractmethod
    def add_person(self, person: Person):
        raise NotImplementedError()
    
    @abstractmethod
    def remove_person(self, person: Person):
        raise NotImplementedError()

    @abstractmethod
    def add_scene_obj(self, obj: SceneObj):
        raise NotImplementedError()
    
    @abstractmethod
    def remove_scene_obj(self, obj: SceneObj):
        raise NotImplementedError()
    
    @abstractmethod
    def without_attention_timedelta(self) -> timedelta:
        raise NotImplementedError()

    @abstractmethod
    def set_without_attention_timedelta(self, tdelta:timedelta):
        raise NotImplementedError()
    
    @abstractmethod
    def until_error_progress(self, current_timestamp:datetime) -> float:
        raise NotImplementedError()
    
    @abstractmethod
    def time_util_error(self, current_timestamp:datetime) -> timedelta:
        raise NotImplementedError()
    
    @abstractmethod
    def last_refresh_timestamp(self) -> datetime:
        raise NotImplementedError()

    @abstractmethod
    def set_last_refresh_timestamp(self, timestamp:datetime):
        raise NotImplementedError()
    

class AttentionScene(QObject):
    person_created = Signal(Person)
    person_removed = Signal(Person)
    attention_rule_created = Signal(AttentionRule)
    attention_rule_removed = Signal(AttentionRule)
    updated = Signal()

    @abstractmethod
    def persons(self) -> list[Person]:
        raise NotImplementedError()
    
    @abstractmethod
    def scene_objs(self) -> list[SceneObj]:
        raise NotImplementedError()
    
    @abstractmethod
    def attention_rules(self) -> list[AttentionRule]:
        raise NotImplementedError()
    
    @abstractmethod
    def create_person(self) -> Person:
        raise NotImplementedError()

    @abstractmethod
    def create_attention_rule(self) -> AttentionRule:
        raise NotImplementedError()
    
    @abstractmethod
    def scene_objs_by_id(self)->dict[Any, SceneObj]:
        raise NotImplementedError()
    
    @abstractmethod
    def persons_by_id(self)->dict[Any, Person]:
        raise NotImplementedError()
    
    @abstractmethod
    def attention_rules_by_id(self)->dict[Any, AttentionRule]:
        raise NotImplementedError()
    
    @abstractmethod
    def export_description(self) -> AttentionSceneDescription:
        raise NotImplementedError()
    
    @abstractmethod
    def export_state(self) -> AttentionSceneState:
        raise NotImplementedError()
    
    @abstractmethod
    def update_with_state(self, state:AttentionSceneState) -> None:
        raise NotImplementedError()

    @abstractmethod
    def trigger_update(self, timestamp:datetime):
        raise NotImplementedError()
    
    @abstractmethod
    def timer(self) -> SceneUpdateTimer:
        raise NotImplementedError()
    
    @abstractmethod
    def set_timer(self, timer:SceneUpdateTimer):
        raise NotImplementedError()
    
