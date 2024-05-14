from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any, TypeGuard, cast
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QColor, QVector3D, QQuaternion
from dataclasses import dataclass
from datetime import timedelta, datetime
import numpy as np
import pandas as pd
from common.domain.scene_timer import RealTimeSceneUpdateTimer, SceneUpdateTimer
from common.dtos.descriptions import AttentionRuleDescription, AttentionSceneDescription, PersonDescription, SceneObjDescription
from common.dtos.head_data import HeadData
from common.dtos.hits import PerformedRayCastResult, AggregatedHit, SceneObjAttentionHits
from common.dtos.states import AttentionRuleState, AttentionSceneState, PersonState, SceneObjState

from .interfaces import AttentionRule, AttentionScene, Person, SceneElement, SceneObj

def quaternions_are_close(q1, q2, tolerance=1e-4):
    dot = QQuaternion.dotProduct(q1, q2)
    print('abs(dot) > 1 - tolerance', abs(dot) > 1 - tolerance)
    return abs(dot) > 1 - tolerance


class ElementModel(SceneElement):
    child_element_added = Signal(object)
    child_element_removed = Signal(object)
    
    added_to_parent_element = Signal(object)
    removed_from_parent_element = Signal(object)

    _some_parent_selected_changed = Signal(bool)
    _some_parent_errored_changed = Signal(bool)

    def __init__(self, element_id:Any, element_name:str, scene:'AttentionSceneModel', parent=None):
        super().__init__(parent)
        self.state_changed = None
        self._element_id = element_id
        self._element_name = element_name
        self._parent_elements:set[ElementModel] = set()
        self._child_elements:set[ElementModel] = set()
        
        self._is_removed_from_scene = False

        self._is_selected = False
        self._is_errored = False
        self._is_tracking = True

        self._cached_some_parent_selected = False
        self._cached_some_parent_errored = False
        
        self._scene:AttentionSceneModel = scene

    def scene(self):
        return self._scene

    def element_id(self):
        return self._element_id

    def element_name(self):
        return self._element_name
    
    def is_removed_from_scene(self):
        return self._is_removed_from_scene
    
    def set_element_name(self, new_name):
        new_name = str(new_name)
        old_name = self._element_name
        self._element_name = new_name
        if old_name != new_name:
            self.element_name_changed.emit(new_name)

    def __contains__(self, model:SceneElement):
        return model in self._child_elements

    def remove_from_scene(self):
        """
        Делает самоудаление из scene (Сцена будет ругаться в случае, если это SceneObjModel)
        Потом удаляет себя из всех предков и потомков
        И в конце подает сигнал, о том что удалён
        """
        self._scene.remove_element(self)
        self._is_removed_from_scene = True

        for parent in list(self._parent_elements):
            parent.remove_child_element(self)
        for child in list(self._child_elements):
            self.remove_child_element(child)
        self.removed_from_scene.emit()

    def _ravel_parents(self):
        res = list(self._parent_elements)
        for parent in self._parent_elements:
            res.extend(parent._ravel_parents())
        return res
    
    def _ravel_children(self):
        res = list(self._child_elements)
        for parent in self._child_elements:
            res.extend(parent._ravel_children())
        return res

    def is_selected(self):
        return self._is_selected

    def is_errored(self):
        return self._is_errored
    
    def is_tracking(self):
        return self._is_tracking

    def has_selected_state(self):
        return self._is_selected or self._cached_some_parent_selected
    
    def has_errored_state(self):
        return self._is_errored or self._cached_some_parent_errored
    
    def has_tracking_state(self):
        raise NotImplementedError()
    
    def set_selected(self, val):
        val = bool(val)
        if self._is_selected != val:
            self._is_selected = val
            self.is_selected_changed.emit(val)

    def set_errored(self, val):
        val = bool(val)
        if self._is_errored != val:
            self._is_errored = val
            self.is_errored_changed.emit(val)
    
    def set_tracking(self, val):
        val = bool(val)
        if self._is_tracking != val:
            self._is_tracking = val
            self.is_tracking_changed.emit(val)
    
    def add_child_element(self, child_element: 'ElementModel'):
        if child_element in self._child_elements:
            return
        """
        При добавлении child элемента, автоматически подвязываются сигналы удаления 
        """
        # make some checking
        self.before_add_child(child_element)
        child_element.before_add_to_parent(self)

        # update collections
        self._child_elements.add(child_element)
        child_element._parent_elements.add(self)

        self.is_selected_changed.connect(child_element._handle_some_parent_selected_changed)
        self._some_parent_selected_changed.connect(child_element._handle_some_parent_selected_changed)

        self.is_errored_changed.connect(child_element._handle_some_parent_errored_changed)
        self._some_parent_errored_changed.connect(child_element._handle_some_parent_errored_changed)

        # fire signal of adding
        self.child_element_added.emit(child_element)
        child_element.added_to_parent_element.emit(self)

        child_element._update_some_parent_selected()
        child_element._update_some_parent_errored()

    @Slot(bool)
    def _handle_some_parent_selected_changed(self, val:bool):
        if self._cached_some_parent_selected != val:
            self._cached_some_parent_selected = val
            self._some_parent_selected_changed.emit(val)

    @Slot(bool)
    def _handle_some_parent_errored_changed(self, val:bool):
        if self._cached_some_parent_errored != val:
            self._cached_some_parent_errored = val
            self._some_parent_errored_changed.emit(val)

    def before_add_to_parent(self, parent:'ElementModel'):
        raise NotImplementedError(f'{self} does not support parent adding')
    
    def before_add_child(self, child:'ElementModel'):
        raise NotImplementedError(f'{self} does not support child adding')

    def remove_child_element(self, child_element: 'ElementModel'):
        try:
            # removed inner connection
            self._child_elements.remove(child_element)
            child_element._parent_elements.remove(self)

            # disconnet signals in both directions
            self.disconnect(child_element)
            child_element.disconnect(self)

            # and notify both of them
            self.child_element_removed.emit(child_element)
            child_element.removed_from_parent_element.emit(self)

            child_element._update_some_parent_selected()
            child_element._update_some_parent_errored()

        except KeyError as e:
            raise RuntimeError(f'Cannot remove child element that was not added, {e}')
    
    def _update_some_parent_selected(self):
        old_val = self._cached_some_parent_selected
        self._cached_some_parent_selected = any([parent._is_selected for parent in self._ravel_parents()])
        if old_val != self._cached_some_parent_selected:
            self._some_parent_selected_changed.emit(self._cached_some_parent_selected)
    
    def _update_some_parent_errored(self):
        old_val = self._cached_some_parent_errored
        self._cached_some_parent_errored = any([parent._is_errored for parent in self._ravel_parents()])
        if old_val != self._cached_some_parent_errored:
            self._some_parent_errored_changed.emit(self._cached_some_parent_errored)


class SceneObjModel(ElementModel, SceneObj):
    NUM_HITS_PER_CASTER = 10
    EXPECTED_CASTS_PER_SECOND = 25
    MIN_CASTS_DENSITY_TO_AQUIRE_ATTENTION = 0.1

    def __init__(self, element_id:str, element_name:str, scene:'AttentionSceneModel', parent=None):
        super().__init__(element_id, element_name, scene, parent)
        self._keep_attention_timedelta = timedelta(seconds=1)
        self._timestamp2aggregated_attention_hits:dict[datetime, AggregatedHit] = dict()
        self._person_id2attention_hits:dict[int, list[tuple[datetime, int]]] = dict()
        self.removed_from_parent_element.connect(self._handle_removed_from_parent)
        self.added_to_parent_element.connect(self._handle_added_to_parent)

    def keep_attention_timedelta(self):
        return self._keep_attention_timedelta
    
    def set_keep_attention_timedelta(self, val:timedelta):
        if val.total_seconds() < 0:
            val = timedelta()
        old_val = self._keep_attention_timedelta
        self._keep_attention_timedelta = val
        if old_val != val:
            self.keep_attention_timedelta_changed.emit(val)

    def before_add_to_parent(self, parent: ElementModel):
        if not isinstance(parent, AttentionRuleModel):
            raise TypeError('Should not add SceneObjModel anywhere, except in AttentionRuleModel')
        
    @Slot(object)
    def _handle_added_to_parent(self, parent:ElementModel):
        assert isinstance(parent, AttentionRuleModel)
        self.added_to_rule.emit(parent)
    
    @Slot(object)
    def _handle_removed_from_parent(self, parent:ElementModel):
        assert isinstance(parent, AttentionRuleModel)
        self.removed_from_rule.emit(parent)
    
    def rules(self) -> list[AttentionRule]:
        return cast(list[AttentionRule], list(self._parent_elements)) 

    def register_attention(self, attention_hit:SceneObjAttentionHits) -> None:
        if attention_hit.person_id not in self._person_id2attention_hits:
            self._person_id2attention_hits[attention_hit.person_id] = [(attention_hit.timestamp, len(attention_hit.hit_poses_local))]
        else:
            self._person_id2attention_hits[attention_hit.person_id].append((attention_hit.timestamp, len(attention_hit.hit_poses_local)))
        self.registered_attention.emit(attention_hit)

    def process_hits_aggregation(self, current_timestamp:datetime) -> None:
        aggregated_hits:list[AggregatedHit] = []
        
        total_seconds = self._keep_attention_timedelta.total_seconds()
        num_hits_threshold = total_seconds * self.NUM_HITS_PER_CASTER * self.EXPECTED_CASTS_PER_SECOND * self.MIN_CASTS_DENSITY_TO_AQUIRE_ATTENTION
        # print(f'{self.element_name()=} {num_hits_threshold=} {self._keep_attention_timedelta=}', end=' ')
        keep_delta = self._keep_attention_timedelta

        for person_id, timestamp_num_hits_pairs in self._person_id2attention_hits.items():
            timestamps = [pair[0] for pair in timestamp_num_hits_pairs]
            hits_per_timestamp = [pair[1] for pair in timestamp_num_hits_pairs]
            # print(f'{hits_per_timestamp=}', end=' ')
            running_num_hits = pd.Series(data=hits_per_timestamp, index=pd.to_datetime(timestamps)).sort_index().\
                                            rolling(keep_delta, min_periods=1).sum()
            
            estimated_max_hits_per_keep_delta = running_num_hits.max()
            estimated_max_hits_timestamp = timestamps[running_num_hits.argmax()]
            # print(f'{estimated_max_hits_per_keep_delta=}', end=' ')
            if estimated_max_hits_per_keep_delta >= num_hits_threshold:
                aggregated_hits.append(AggregatedHit(estimated_max_hits_timestamp, person_id))
        # print()
        self._filter_outdated_attention_hits(current_timestamp - self._keep_attention_timedelta)
        if aggregated_hits:
            self.set_aggregated_hits(aggregated_hits)

    def set_aggregated_hits(self, hits:list[AggregatedHit]):
        added_hits:list[AggregatedHit] = []
        for hit in hits:
            if hit.timestamp not in self._timestamp2aggregated_attention_hits:
                self._timestamp2aggregated_attention_hits
                added_hits.append(hit)
        if added_hits:
            self.aggregated_attention_hits_added.emit(added_hits)
            self.aggregated_attention_hits_changed.emit()
        
    def filter_outdated_aggregated_hits(self, keep_timestamp:datetime):
        new_aggreagated_hits = {timestamp:hit for timestamp, hit in self._timestamp2aggregated_attention_hits.items() if timestamp >= keep_timestamp}
        if len(self._timestamp2aggregated_attention_hits) != new_aggreagated_hits:
            self._timestamp2aggregated_attention_hits = new_aggreagated_hits
            self.aggregated_attention_hits_changed.emit()
    
    def _filter_outdated_attention_hits(self, keep_timestamp:datetime):
        new_person_id2attention_hits:dict[int, list[tuple[datetime, int]]] = dict()
        for person_id, hits_data in self._person_id2attention_hits.items():
            not_outdated_hits_data = list(filter(lambda hit_data: hit_data[0] > keep_timestamp, hits_data))
            if not_outdated_hits_data:
                new_person_id2attention_hits[person_id] = not_outdated_hits_data

        self._person_id2attention_hits = new_person_id2attention_hits

    def aggregated_hits(self) -> list[AggregatedHit]:
        return list(self._timestamp2aggregated_attention_hits.values())

    def attention_accumulation_progress(self, current_time:datetime):
        num_hits_threshold = self.NUM_HITS_PER_CASTER * self.EXPECTED_CASTS_PER_SECOND * self.MIN_CASTS_DENSITY_TO_AQUIRE_ATTENTION
        
        keep_delta = self._keep_attention_timedelta
        max_progress = 0
        for person, timestamp_num_hits_pairs in self._person_id2attention_hits.items():
            precending_to_current_timestamp_pairs = list(filter(lambda pair: pair[0] < current_time, timestamp_num_hits_pairs))
            timestamps = [pair[0] for pair in precending_to_current_timestamp_pairs]
            hits_per_timestamp = [pair[1] for pair in precending_to_current_timestamp_pairs]
            if len(precending_to_current_timestamp_pairs) > 0:
                running_mean_num_hits = pd.Series(data=hits_per_timestamp, index=pd.to_datetime(timestamps)).sort_index().\
                                                rolling(keep_delta, min_periods=1).sum()
                
                estimated_max_hits_per_keep_delta = running_mean_num_hits.max()
                max_progress = min(max(max_progress, estimated_max_hits_per_keep_delta / num_hits_threshold), 1)
        
        return max_progress


class PersonModel(ElementModel, Person):
    def __init__(self, 
                 head_color:QColor,
                 camera_position: QVector3D,
                 camera_rotation: QQuaternion,
                 person_id:int, name, scene:'AttentionSceneModel'):
        super().__init__(person_id, name, scene)
        self._head_color = head_color
        self._camera_position = camera_position
        self._camera_rotation = camera_rotation
        self._head_data = HeadData()
        self.added_to_parent_element.connect(self._handle_added_to_parent)
        self.removed_from_parent_element.connect(self._handle_removed_from_parent)
        self._performed_ray_cast_result:PerformedRayCastResult|None = None

        if not isinstance(head_color, QColor):
            raise TypeError()

        if not isinstance(camera_position, QVector3D):
            raise TypeError(f'camera_position should QVector3D, got {self._camera_position}')
        
        if not isinstance(camera_rotation, QQuaternion):
            raise TypeError(f'camera_position should be QQuaternion, got {self._camera_position}')
        
        self.set_head_color(head_color)
        self.set_camera_rotation(camera_rotation)
        self.set_camera_position(camera_position)
    
    @Slot(object)
    def _handle_added_to_parent(self, parent:ElementModel):
        assert isinstance(parent, AttentionRuleModel)
        self.added_to_rule.emit(parent)
    
    def performed_ray_cast_result(self) -> PerformedRayCastResult|None:
        return self._performed_ray_cast_result

    def set_performed_ray_cast_result(self, cast_result:PerformedRayCastResult):
        self._performed_ray_cast_result = cast_result
        self.performed_ray_cast_result_changed.emit()

        scene_obj_grouping:dict[Any, tuple[list[QVector3D], list[QVector3D]]] = dict()

        for scene_obj_id, w, l in zip(cast_result.scene_obj_ids, cast_result.hits_global, cast_result.hits_local):
            if scene_obj_id not in scene_obj_grouping:
                scene_obj_grouping[scene_obj_id] = ([], [])
            scene_obj_grouping[scene_obj_id][0].append(w)
            scene_obj_grouping[scene_obj_id][1].append(l)
        
        scene_objs_by_id = self._scene.scene_objs_by_id()

        for scene_obj_id, hit_poses in scene_obj_grouping.items():
            attenion_hits = SceneObjAttentionHits(timestamp=cast_result.timestamp,
                                  person_id=self.element_id(),
                                  scene_obj_id=scene_obj_id,
                                  hit_poses_global=hit_poses[0],
                                  hit_poses_local=hit_poses[1]
                                  )

            if scene_obj := scene_objs_by_id.get(scene_obj_id):
                scene_obj.register_attention(attenion_hits)
    
    @Slot(object)
    def _handle_removed_from_parent(self, parent:ElementModel):
        assert isinstance(parent, AttentionRuleModel)
        self.removed_from_rule.emit(parent)

    def before_add_to_parent(self, parent: ElementModel):
        if not isinstance(parent, AttentionRuleModel):
            raise TypeError('Should not add PersonModel anywhere, except in AttentionRuleModel')

    def rules(self) -> list[AttentionRule]:
        return cast(list[AttentionRule], list(self._parent_elements))    

    def head_color(self):
        return self._head_color

    def set_head_color(self, color:QColor):
        if not isinstance(color, QColor):
            raise TypeError(f'Expected QColor, got {color}')

        if color != self._head_color:
            self._head_color = color
            self.head_color_changed.emit(self._head_color)

    def camera_position(self):
        return self._camera_position

    def set_camera_position(self, position:QVector3D):
        if not isinstance(position, QVector3D):
            raise TypeError(f'Expected QVector3D, got {position}')
        
        if position != self._camera_position:
            self._camera_position = position
            self.camera_position_changed.emit(position)

    def camera_rotation(self):
        return self._camera_rotation

    def set_camera_rotation(self, rotation:QQuaternion):
        if not isinstance(rotation, QQuaternion):
            raise TypeError(f'Expected QQuaternion, got {rotation}')
        rotation.normalize()
        
        if not quaternions_are_close(rotation, self._camera_rotation):
            self._camera_rotation = rotation
            self.camera_rotation_changed.emit(rotation) 

    def head_data(self, ) -> HeadData:
        return self._head_data

    @Slot(HeadData)
    def set_head_data(self, data:HeadData):
        if self._head_data != data and data.timestamp > self._head_data.timestamp:
            self._head_data = data    
            self.head_data_changed.emit(data)


class AttentionRuleModel(AttentionRule, ElementModel):
    def __init__(self, element_id, element_name, without_attention_timedelta:timedelta, scene, parent=None):
        super().__init__(element_id, element_name, scene, parent)

        self._without_attention_timedelta = timedelta(minutes=1)
        self._last_refresh_timestamp:datetime = self.scene().timer().now()
        self.child_element_added.connect(self._handle_child_added)
        self.child_element_removed.connect(self._handle_child_removed)
        self.set_without_attention_timedelta(without_attention_timedelta)
    
    def without_attention_timedelta(self):
        return self._without_attention_timedelta

    def set_without_attention_timedelta(self, tdelta:timedelta):
        assert isinstance(tdelta, timedelta)
        old_tdelta = self._without_attention_timedelta
        if tdelta.total_seconds() < 0:
            self._without_attention_timedelta = timedelta()
        else:
            self._without_attention_timedelta = tdelta
        if old_tdelta != self._without_attention_timedelta:
            self.without_attention_timedelta_changed.emit(self._without_attention_timedelta)

    def before_add_child(self, child: ElementModel):
        if not isinstance(child, (PersonModel, SceneObjModel)):
            raise TypeError(f'expected child of type PersonModel or SceneObjModel, recieved {child} of type {type(child)}')

    def before_add_to_parent(self, parent: ElementModel):
        raise NotImplementedError('AttentionRuleModel may not have parent element')

    @Slot(object)
    def _handle_child_added(self, child:ElementModel):
        if isinstance(child, PersonModel):
            self.person_added.emit(child)
        elif isinstance(child, SceneObjModel):
            child.aggregated_attention_hits_changed.connect(self._handle_aggregated_hits)
            self.scene_obj_added.emit(child)
    
    @Slot(object)
    def _handle_child_removed(self, child:ElementModel):
        if isinstance(child, PersonModel):
            self.person_removed.emit(child)
        elif isinstance(child, SceneObjModel):
            self.scene_obj_removed.emit(child)
    
    def persons(self) -> list[Person]:
        def is_person(el:object) -> TypeGuard[Person]:
            return isinstance(el, Person)
        filtered = filter(is_person, self._child_elements)
        return list(filtered) # return first matching or None

    def scene_objs(self) -> list[SceneObj]:
        def is_scene_obj(el:object) -> TypeGuard[SceneObj]:
            return isinstance(el, SceneObj)
        filtered = filter(is_scene_obj, self._child_elements)
        return list(filtered) # return first matching or None

    def time_util_error(self, current_timestamp:datetime) -> timedelta:
        """
        Возвращает время, через которое произойдет ошибка, если внимание не будет зарегистрировано
        Если начальная точка отсчета не сгенерирована, то время до ошибки не определено
        Возвращенное значение может быть отрицательным, что означает, что ошибка уже произвошла и прошло столько-то времени с этого события
        """
        would_be_error_timestamp = self._last_refresh_timestamp + self._without_attention_timedelta
        time_until_error = would_be_error_timestamp - current_timestamp

        return time_until_error
    
    def until_error_progress(self, current_timestamp:datetime) -> float:
        seconds_left = (self.time_util_error(current_timestamp) or timedelta()).total_seconds()
        total_seconds = self.without_attention_timedelta().total_seconds()
        if total_seconds == 0:
            return 0
        return seconds_left / total_seconds

    def last_refresh_timestamp(self) -> datetime:
        return self._last_refresh_timestamp

    def set_last_refresh_timestamp(self, timestamp:datetime):
        if self._last_refresh_timestamp is None or self._last_refresh_timestamp < timestamp:
            self._last_refresh_timestamp = timestamp
            self.last_refresh_timestamp_changed.emit(timestamp)        
        self.compute_error_state()

    def compute_error_state(self):
        time_until_error = self.time_util_error(self._scene.timer().now())
        # print(f'{time_until_error=}')
        self.set_errored(time_until_error.total_seconds() < 0)

    @Slot()
    def _handle_aggregated_hits(self) -> None:
        if not self.is_tracking():
            return
        scene_obj = self.sender()
        if not isinstance(scene_obj, SceneObjModel):
            return
        aggregated_hits = scene_obj.aggregated_hits()
        persons = self.persons()
        if not persons:
            return
        
        persons_ids = set(map(lambda p: p.element_id(),persons))
        matched_persons_timestamps:list[datetime] = [hit.timestamp for hit in aggregated_hits if hit.person_id in persons_ids]
        
        if matched_persons_timestamps:
            latest_match = max(matched_persons_timestamps)
            print(f'{self._scene.timer().now()} {latest_match=}')
            self.set_last_refresh_timestamp(latest_match)
    
    def add_person(self, person:Person):
        if not isinstance(person, PersonModel):
            raise TypeError()
        self.add_child_element(person)

    def remove_person(self, person:Person):
        if not isinstance(person, PersonModel):
            raise TypeError()
        self.remove_child_element(person)

    def add_scene_obj(self, scene_obj:SceneObj):
        if not isinstance(scene_obj, SceneObjModel):
            raise TypeError()
        self.add_child_element(scene_obj)
    
    def remove_scene_obj(self, scene_obj:SceneObj):
        if not isinstance(scene_obj, SceneObjModel):
            raise TypeError()
        self.remove_child_element(scene_obj)


class AttentionSceneModel(AttentionScene):
    def __init__(self,
                 scene_obj_ids:list[str],
                 parent=None) -> None:
        super().__init__(parent)
        self._person_models:list[PersonModel] = list()
        self._scene_obj_models:list[SceneObjModel] = [SceneObjModel(_id, _id, self, self) for _id in scene_obj_ids]
        self._timer:SceneUpdateTimer = RealTimeSceneUpdateTimer()
        self._attention_rule_models:list[AttentionRuleModel] = list()

        self._reserved_numeric_ids:set[int] = set()

    def _generate_new_id(self):
        if len(self._reserved_numeric_ids) == 0:
            id = 0
        else:
            id = max(self._reserved_numeric_ids) + 1
        self._reserve_numeric_id(id)
        return id

    def _reserve_numeric_id(self, id):
        if id in self._reserved_numeric_ids:
            raise ValueError(f'Cannot reserver id:{id}, it was already reserved')
        self._reserved_numeric_ids.add(id)

    def create_person(self):
        new_person_model = PersonDescription(id=self._generate_new_id(),
                                                  name='Новый пользователь',
                                                  head_color=np.random.randint(0, 255, 3).tolist(),
                                                  camera_position=QVector3D(),
                                                  camera_rotation=QQuaternion())
        self._create_person_from_description(new_person_model)

    def create_restored_person(self, description:PersonDescription):
        self._create_person_from_description(description, is_restored=True)

    def _create_person_from_description(self, description:PersonDescription, is_restored=False):
        for person in self._person_models:
            if person.element_id() == description.id:
                raise ValueError(f'Cannot create second person with id={description.id}')
        if is_restored:
            self._reserve_numeric_id(description.id)
        person = PersonModel(head_color=description.head_color,
                             camera_position=description.camera_position,
                             camera_rotation=description.camera_rotation,
                             person_id=description.id,
                             name=description.name,
                             scene=self)
        
        self._person_models.append(person)
        self.person_created.emit(person)

    def create_attention_rule(self):
        _id = self._generate_new_id()
        new_attention_rule_description = AttentionRuleDescription(_id, f'Новое правило #{_id}', 60, [], [])
        self._create_attention_rule_from_description(new_attention_rule_description)

    def create_restored_attention_rule(self, description:AttentionRuleDescription):
        self._create_attention_rule_from_description(description, is_restored=True)

    def _create_attention_rule_from_description(self, description:AttentionRuleDescription, is_restored=False):
        if description.id in self.attention_rules_by_id():
            raise ValueError(f'Cannot create second rule with id={description.id}')
        
        person_by_id = self.persons_by_id()
        scene_obj_by_id = self.scene_objs_by_id()

        if is_restored:
            self._reserve_numeric_id(description.id)
        
        attention_rule = AttentionRuleModel(description.id, 
                                            description.name, 
                                            description.without_attention_timedelta,
                                            self, self)
        self._attention_rule_models.append(attention_rule)
        self.attention_rule_created.emit(attention_rule)

        for person_id in description.person_ids:
            person = person_by_id.get(person_id, None)
            if person is None:
                raise KeyError(f'Could not find PersonModel with id={person_id}')
            
            attention_rule.add_child_element(person)

        for scene_obj_id in description.scene_obj_ids:
            scene_obj = scene_obj_by_id.get(scene_obj_id, None)
            if scene_obj is None:
                  raise KeyError(f'Could not find SceneObjModel with id={person_id}')
            attention_rule.add_child_element(scene_obj)

    def persons(self, ) -> list[Person]:
        return list(self._person_models)

    def scene_objs(self, ) -> list[SceneObj]:
        return list(self._scene_obj_models)

    def attention_rules(self, ) -> list[AttentionRule]:
        return list(self._attention_rule_models)
    
    def timer(self) -> SceneUpdateTimer:
        return self._timer
    
    def set_timer(self, timer:SceneUpdateTimer):
        self._timer.disconnect(self)
        self._timer = timer
        self._timer.triggered_scene_update.connect(self._triggered_scene_update)

    @Slot()
    def _triggered_scene_update(self):
        self.trigger_update(self._timer.now())

    def remove_element(self, element:ElementModel):
        if isinstance(element, SceneObjModel):
            raise RuntimeError("You may not remove SceneObjModel from scene. If that a case, remoe it in your 3d editor")
        elif isinstance(element, PersonModel):
            self._person_models.remove(element)
            self.person_removed.emit(element)
        elif isinstance(element, AttentionRuleModel):
            self._attention_rule_models.remove(element)
            self.attention_rule_removed.emit(element)

    def export_state(self) -> AttentionSceneState:
        person_states = [
            PersonState(person.element_id(), 
                                   person.element_name(),
                                   person.head_color(),
                                   person.camera_position(),
                                   person.camera_rotation(),
                                   person.head_data(), 
                                   person.performed_ray_cast_result())
            for person in self._person_models
        ]

        scene_objs_states = [
            SceneObjState(scene_obj.element_id(),
                            scene_obj.element_name(),
                            scene_obj.keep_attention_timedelta(),
                            scene_obj.aggregated_hits())
            for scene_obj in self._scene_obj_models
        ]
        
        rule_states = [
            AttentionRuleState(rule.element_id(), 
                                     rule.element_name(),
                                     rule.without_attention_timedelta().total_seconds(),
                                     [person.element_id() for person in rule.persons()],
                                     [scene_obj.element_id() for scene_obj in rule.scene_objs()],
                                     rule.last_refresh_timestamp())
            for rule in self._attention_rule_models
        ]

        scene_state = AttentionSceneState(
            scene_objs=scene_objs_states,
            persons=person_states,
            rules=rule_states)
        return scene_state
    
    def update_with_state(self, scene_state:AttentionSceneState):
        persons_by_id = self.persons_by_id()
        for person_state in scene_state.persons:
            person = persons_by_id[person_state.id]
            person.set_head_data(person_state.head_data)
            person.set_element_name(person_state.name)
            person.set_camera_position(person_state.camera_position)
            person.set_camera_rotation(person_state.camera_rotation)
            person.set_head_color(person_state.head_color)
            person.set_head_data(person_state.head_data)
            if person_state.last_cast_result:
                person.set_performed_ray_cast_result(person_state.last_cast_result)

        scene_objs_by_id = self.scene_objs_by_id()
        for scene_obj_state in scene_state.scene_objs:
            scene_obj = scene_objs_by_id[scene_obj_state.id]
            scene_obj.set_element_name(scene_obj_state.name)
            scene_obj.set_keep_attention_timedelta(scene_obj_state.keep_attention_timedelta)
            scene_obj.set_aggregated_hits(scene_obj_state.aggregated_hits)
        
        rules_by_id = self.attention_rules_by_id()
        for rule_state in scene_state.rules:
            rule = rules_by_id[rule_state.id]
            rule.set_last_refresh_timestamp(rule_state.last_refresh_timestamp)
            rule.set_element_name(rule_state.name)
            rule.set_without_attention_timedelta(rule_state.without_attention_timedelta)

    def export_description(self) -> AttentionSceneDescription:
        person_descriptions = [
            PersonDescription(person.element_id(), 
                                   person.element_name(),
                                   person.head_color(),
                                   person.camera_position(),
                                   person.camera_rotation())
            for person in self._person_models
        ]

        scene_objs_descriptions = [
            SceneObjDescription(scene_obj.element_id(),
                                     scene_obj.element_name(),
                                     scene_obj.keep_attention_timedelta())
            for scene_obj in self._scene_obj_models
        ]
        
        rules_descriptions = [
            AttentionRuleDescription(rule.element_id(), 
                                     rule.element_name(),
                                     rule.without_attention_timedelta().total_seconds(),
                                     [person.element_id() for person in rule.persons()],
                                     [scene_obj.element_id() for scene_obj in rule.scene_objs()])
            for rule in self._attention_rule_models
        ]

        scene_description = AttentionSceneDescription(
            scene_objs=scene_objs_descriptions,
            persons=person_descriptions,
            rules=rules_descriptions
        )
        return scene_description

    
    def trigger_update(self, timestamp:datetime):
        # timedeltas = [rule.without_attention_timedelta() for rule in self._attention_rule_models] +\
        #       [scene_obj.keep_attention_timedelta() for scene_obj in self._scene_obj_models] + [timedelta(seconds=1)]
        timedeltas = [scene_obj.keep_attention_timedelta() for scene_obj in self._scene_obj_models] + [timedelta(seconds=20)]
        max_time_delta = max(*timedeltas)
        outdate_timestamp = timestamp - max_time_delta*2
        
        # for rule in self.attention_rules():
        #     rule.set_last_refresh_timestamp(timestamp)

        for scene_obj in self._scene_obj_models:
            scene_obj.process_hits_aggregation(timestamp)
            scene_obj.filter_outdated_aggregated_hits(outdate_timestamp)

        self.updated.emit()

        

    def scene_objs_by_id(self):
        return {scene_obj.element_id():scene_obj for scene_obj in self._scene_obj_models}

    def persons_by_id(self):
        return {person.element_id():person for person in self._person_models}
    
    def attention_rules_by_id(self):
        return {rule.element_id():rule for rule in self._attention_rule_models}