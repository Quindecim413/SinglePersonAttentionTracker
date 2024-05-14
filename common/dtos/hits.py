from datetime import datetime
from pydantic import TypeAdapter, model_validator
from pydantic.dataclasses import dataclass

from common.dtos.utils import BaseConfig, PersonId, SceneObjId, Vec3D


@dataclass(frozen=True, config=BaseConfig)
class SceneObjAttentionHits:
    timestamp:datetime
    person_id:int
    scene_obj_id:str
    hit_poses_global:list[Vec3D]
    hit_poses_local:list[Vec3D]

    @model_validator(mode='after') # type: ignore
    def validate_shape_match(self):
        if not (len(self.hit_poses_global) == len(self.hit_poses_local)):
            raise ValueError("Lenght's of hit_poses_global and hit_poses_local should be the same")
        return self

@dataclass(frozen=True, config=BaseConfig)
class AggregatedHit:
    timestamp:datetime
    person_id:int

@dataclass(frozen=True, config=BaseConfig)
class SceneObjAggregatedHits:
    scene_obj_id:SceneObjId
    hits:list[AggregatedHit]

@dataclass(frozen=True, config=BaseConfig)
class PerformedRayCastResult:
    timestamp:datetime
    scene_obj_ids:list[str]
    hits_global:list[Vec3D]
    hits_local:list[Vec3D]

    @model_validator(mode='after') # type: ignore
    def validate_shape_match(self):
        if not (len(self.scene_obj_ids) == len(self.hits_global) == len(self.hits_local)):
            raise ValueError("Lenght's of scene_obj_ids, hits_global and hits_local should be the same")
        return self
    
@dataclass(frozen=True, config=BaseConfig)
class PersonPerformedRayCastResult:
    person_id:PersonId
    cast_result:PerformedRayCastResult

SceneObjAttentionHitsAdapter = TypeAdapter(SceneObjAttentionHits)
SceneObjAggregatedHitsAdapter = TypeAdapter(SceneObjAggregatedHits)
PerformedRayCastResultAdapter = TypeAdapter(PerformedRayCastResult)
PersonPerformedRayCastResultAdapter = TypeAdapter(PersonPerformedRayCastResult)