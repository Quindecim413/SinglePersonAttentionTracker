#!/usr/bin/python
#-*- coding: utf-8 -*-
from __future__ import annotations
from collections import defaultdict
from enum import Enum
import enum
import logging
from math import e
from pathlib import Path
from turtle import right
from typing import TypeAlias, TypeGuard, cast
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QUrl, QPointF, QPoint
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QColor, QVector3D, QQuaternion
from dataclasses import dataclass
from datetime import timedelta, datetime
import numpy as np
from functools import partial
import traceback
from common.domain.interfaces import Person, SceneObj
from common.dtos.head_data import EyesTransforms
from common.dtos.head_data import HeadData, HeadProps
from common.dtos.hits import PerformedRayCastResult
from common.rays_casting.casters import AggregatedCastResult, MultipleRayCastersEntity

from common.services.scene.caster_pointer import CasterPointerEntity
from common.services.scene.hit_3d_point import Hit3DPoint
from common.widgets.render_window import RenderWindow


vec3:TypeAlias = tuple[float, float, float]

class ViewState(Enum):
    Plain=0
    Selected=1
    Errored=2

src3d = Path(__file__).parent/"src3d"


class SceneObj3dViewComponent(Qt3DCore.QComponent):
    def __init__(self, scene_obj:SceneObj, parent=None) -> None:
        super().__init__(parent)
        self.setShareable(False)
        self._scene_obj = scene_obj
        self._check_ind = 0
        self.addedToEntity.connect(self._handle_added_to_entity)
        self.removedFromEntity.connect(self._handle_removed_from_entity)

        self._errored_material = Qt3DExtras.QPhongMaterial(self)
        self._errored_material.setAmbient(QColor(240, 20, 20))

        self._selected_material = Qt3DExtras.QPhongMaterial(self)
        self._selected_material.setAmbient(QColor(230, 245, 16))
        self._ref_to_base_material:Qt3DRender.QMaterial|None = None

        self._obj_picker = Qt3DRender.QObjectPicker(self)
        self._obj_picker.clicked.connect(self._handle_obj_clicked)
        self._selectable_by_picking = True

    def scene_obj(self) -> SceneObj:
        return self._scene_obj

    @Slot()
    def _handle_obj_clicked(self):
        print('clicked on', self._scene_obj.element_id())
        print(f'SceneObj3DModel {self._selectable_by_picking=}')
        if self._selectable_by_picking:
            self._scene_obj.set_selected(not self._scene_obj.is_selected())

    def selectable_by_picking(self) -> bool:
        return self._selectable_by_picking

    def set_selectable_by_picking(self, val:bool):
        print(f'SceneObj3DModel {self._selectable_by_picking=}')
        val = bool(val)
        if self._selectable_by_picking != val:
            self._selectable_by_picking = val

    @Slot(Qt3DCore.QEntity)
    def _handle_added_to_entity(self, ent:Qt3DCore.QEntity):
        def is_material(c:Qt3DCore.QComponent) -> TypeGuard[Qt3DRender.QMaterial]:
            return isinstance(c, Qt3DRender.QMaterial)
        c = next(filter(is_material, ent.components()))
        self._ref_to_base_material = c
        print(self._ref_to_base_material)
        ent.addComponent(self._obj_picker)
    
    @Slot(Qt3DCore.QEntity)
    def _handle_removed_from_entity(self, ent):
        self._ref_to_base_material = None
        # ent.addComponent(self._obj_picker)

    @Slot(ViewState)
    def update_view_state(self, state:ViewState):
        if self._ref_to_base_material is None:
            return
        match(state):
            case ViewState.Plain:
                material_to_set = self._ref_to_base_material
                materials_to_remove:tuple[Qt3DRender.QMaterial, Qt3DRender.QMaterial] = self._errored_material, self._selected_material
            case ViewState.Errored: 
                if self._scene_obj.has_errored_state():
                    material_to_set = self._errored_material
                    materials_to_remove = self._selected_material, self._ref_to_base_material
                else:
                    material_to_set = self._ref_to_base_material
                    materials_to_remove = self._errored_material, self._selected_material
            case ViewState.Selected:
                if self._scene_obj.has_selected_state():
                    material_to_set = self._selected_material
                    materials_to_remove = self._errored_material, self._ref_to_base_material
                else:
                    material_to_set = self._ref_to_base_material
                    materials_to_remove = self._errored_material, self._selected_material
            case _:
                return
        
        obj_ent = next(iter(self.entities()), None)
        
        if obj_ent:
            if materials_to_remove[0] in obj_ent.components():
                obj_ent.removeComponent(materials_to_remove[0])
            if materials_to_remove[1] in obj_ent.components():
                obj_ent.removeComponent(materials_to_remove[1])
            if material_to_set not in obj_ent.components():
                obj_ent.addComponent(material_to_set)

class SmallMarkerCube(Qt3DCore.QEntity):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cube_mesh = Qt3DRender.QMesh(self)
        self._cube_mesh.setSource(QUrl.fromLocalFile(src3d / 'small_cube.obj'))
        self.addComponent(self._cube_mesh)

        self._material:Qt3DRender.QMaterial = Qt3DExtras.QPhongMaterial()
        self._material.setAmbient(QColor('green'))
        self.addComponent(self._material)

        self._transform = Qt3DCore.QTransform(self)
        self.addComponent(self._transform)
        
    def set_material(self, material:Qt3DRender.QMaterial):
        self.removeComponent(self._material)
        self._material = material
        self.addComponent(self._material)

    def set_position(self, pos:QVector3D):
        self._transform.setTranslation(pos)


class FaceFromCubes(Qt3DCore.QEntity):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cubes = [SmallMarkerCube(self) for _ in range(478)]
        self._transform = Qt3DCore.QTransform()
        self.addComponent(self._transform)
    
    def set_material(self, material:Qt3DRender.QMaterial):
        for p in self._cubes:
            p.set_material(material)

    def set_head_data(self, head_data:HeadData):
        if head_data.head_props:
            self._transform.setTranslation(head_data.head_props.position)
            self._transform.setRotation(head_data.head_props.rotation)
        if head_data.view_origin == HeadData.ViewOrigin.NOT_VISIBLE:
            self.setEnabled(False)
            return
        self.setEnabled(True)
        for marker_cube, kp in zip(self._cubes, cast(HeadProps, head_data.head_props).keypoints):
            pos = QVector3D(*kp)
            marker_cube.set_position(pos)


class Person3DModelEntity(Qt3DCore.QEntity):
    def __init__(self, person:Person,
                 scene_objs_picking_layer:Qt3DRender.QLayer,
                 parent:Qt3DCore.QEntity) -> None:
        super().__init__(parent)
        self._person = person
        self._workspace_transform = Qt3DCore.QTransform(self)
        self.addComponent(self._workspace_transform)

        self._camera = Qt3DCore.QEntity(self)
        self._camera.setObjectName('camera')
        self._camera_loader = Qt3DRender.QSceneLoader(self._camera)
        self._camera.addComponent(self._camera_loader)
        self._camera_loader.setSource(QUrl.fromLocalFile(src3d / "webcam.obj"))
        # self._camera_loader.statusChanged.connect(lambda status: print(status, self._camera_loader.status()))
        self._camera_transform = Qt3DCore.QTransform()
        # self._camera_transform.setRotationY(180)
        self._camera.addComponent(self._camera_transform)

        self._head_entity = Qt3DCore.QEntity(self._camera)
        self._head_entity.setObjectName('Head entity')
        self._head_transform = Qt3DCore.QTransform(self._head_entity)
        self._head_transform.setTranslation(QVector3D(0, 0.2, -0.5))
        self._head_transform.setRotationY(180)
        self._head_entity.addComponent(self._head_transform)

        self._head_mesh = Qt3DRender.QMesh(self._head_entity)
        self._head_mesh.setSource(QUrl.fromLocalFile(src3d / 'canonical head processed.obj'))
        # self._head_mesh.statusChanged.connect(lambda status: print(status, self._head_mesh.status()))
        self._head_mesh_material = Qt3DExtras.QPhongMaterial(self._head_entity)
        self._head_mesh_material.setAmbient(self._person.head_color())
        self._head_entity.addComponent(self._head_mesh)
        self._head_entity.addComponent(self._head_mesh_material)

        self._errored_material = Qt3DExtras.QPhongMaterial(self._head_entity)
        self._errored_material.setAmbient(QColor(240, 20, 20))

        self._selected_material = Qt3DExtras.QPhongMaterial(self._head_entity)
        self._selected_material.setAmbient(QColor(220, 200, 20))

        eye_obj_url = QUrl.fromLocalFile(src3d / 'canonical head eyes.obj')

        self._left_eye = Qt3DCore.QEntity(self._head_entity)
        left_eye_loader = Qt3DRender.QSceneLoader(self._left_eye)
        left_eye_loader.setSource(eye_obj_url)
        self._left_eye.addComponent(left_eye_loader)
        self._left_eye_transform = Qt3DCore.QTransform(self._left_eye)
        self._left_eye_transform.setTranslation(QVector3D(-0.032, 0.025, -0.025))
        self._left_eye.addComponent(self._left_eye_transform)

        self._right_eye = Qt3DCore.QEntity(self._head_entity)
        right_eye_loader = Qt3DRender.QSceneLoader(self._right_eye)
        right_eye_loader.setSource(eye_obj_url)
        self._right_eye.addComponent(right_eye_loader)
        self._right_eye_transform = Qt3DCore.QTransform(self._right_eye)
        self._right_eye_transform.setTranslation(QVector3D(0.032, 0.025, -0.025))
        self._right_eye.addComponent(self._right_eye_transform)

        self._between_eyes = Qt3DCore.QEntity(self._head_entity)
        self._between_eyes_transform = Qt3DCore.QTransform(self._between_eyes)
        self._between_eyes_transform.setTranslation(QVector3D(0, 0.025, -0.025))
        self._between_eyes.addComponent(self._between_eyes_transform)

        self._between_eyes_pointer = CasterPointerEntity(parent=self._between_eyes)
        self._left_eye_pointer = CasterPointerEntity(parent=self._left_eye)
        self._right_eye_pointer = CasterPointerEntity(parent=self._right_eye)

        self._between_eyes_caster = MultipleRayCastersEntity(parent=self._between_eyes)
        self._left_eye_caster = MultipleRayCastersEntity(parent=self._left_eye)
        self._right_eye_caster = MultipleRayCastersEntity(parent=self._right_eye)

        self._attention_hit_points = [Hit3DPoint(self._person.head_color(), self) for _ in range(10)]
        for p in self._attention_hit_points:
            p.setEnabled(False)
        # self._per_point_hit_result:list[tuple[SceneObj, QVector3D, QVector3D]|None] =\
        #         [None for _ in self._attention_hit_points] #hit result in global coord
        
        self._between_eyes_caster.cast_results_aggregated.connect(self.__cast_results_aggregated)
        self._left_eye_caster.cast_results_aggregated.connect(self.__cast_results_aggregated)
        self._right_eye_caster.cast_results_aggregated.connect(self.__cast_results_aggregated)

        self._between_eyes_caster.addLayer(scene_objs_picking_layer)
        self._left_eye_caster.addLayer(scene_objs_picking_layer)
        self._right_eye_caster.addLayer(scene_objs_picking_layer)

        self._person.camera_position_changed.connect(self._handle_camera_position_changed)
        self._person.camera_rotation_changed.connect(self._handle_camera_rotation_changed)
        self._person.head_color_changed.connect(self._handle_head_color_changed)

        self._last_shown_hits_results_timestamp = datetime.now()

        self._person.performed_ray_cast_result_changed.connect(self._handle_hits_performed)

        self._person.head_data_changed.connect(self._handle_person_head_data_changed)

        self._head_from_cubes = FaceFromCubes(self._camera)

        self._obj_picker = Qt3DRender.QObjectPicker(self)
        self._obj_picker.clicked.connect(self._handle_obj_clicked)
        self.addComponent(self._obj_picker)

        self._handle_camera_position_changed(self._person.camera_position())
        self._handle_camera_rotation_changed(self._person.camera_rotation())
        self._handle_head_color_changed(self._person.head_color())

        self._person.removed_from_scene.connect(self._handle_person_removed)
        self._selectable_by_picking = True

    def selectable_by_picking(self) -> bool:
        return self._selectable_by_picking

    def set_selectable_by_picking(self, val:bool):
        val = bool(val)
        if self._selectable_by_picking != val:
            self._selectable_by_picking = val

    @Slot()
    def _handle_obj_clicked(self):
        if self._selectable_by_picking:
            self._person.set_selected(not self._person.is_selected())

    @Slot(HeadData)
    def _handle_person_head_data_changed(self, data:HeadData):
        self._head_from_cubes.set_head_data(data)

        if data.view_origin == HeadData.ViewOrigin.NOT_VISIBLE:
            self._head_entity.setEnabled(False)
            return

        head_props = cast(HeadProps, data.head_props)
        eyes_transforms = cast(EyesTransforms, data.eyes_transforms)

        self._head_entity.setEnabled(True)
        self._head_transform.setTranslation(head_props.position)
        self._head_transform.setRotation(head_props.rotation)

        self._left_eye_transform.setTranslation(eyes_transforms.left_eye_transform.position)
        self._left_eye_transform.setRotation(eyes_transforms.left_eye_transform.rotation)
        
        self._right_eye_transform.setTranslation(eyes_transforms.right_eye_transform.position)
        self._right_eye_transform.setRotation(eyes_transforms.right_eye_transform.rotation)

    @Slot(AggregatedCastResult)
    def __cast_results_aggregated(self, aggregated_cast_result:AggregatedCastResult):
        def is_SceneObj3dViewComponent(c:Qt3DCore.QComponent) -> TypeGuard[SceneObj3dViewComponent]:
            return isinstance(c, SceneObj3dViewComponent)
        
        scene_obj_ids, pos_glob, pos_loc = [], [], []
        for cast_res in aggregated_cast_result.casts:
            if cast_res.is_succesfull:
                cast_hit = cast(Qt3DRender.QRayCasterHit, cast_res.hit)
        
                scene_obj_model_comp = next(filter(is_SceneObj3dViewComponent, cast_hit.entity().components()), None)
                if scene_obj_model_comp:
                    pos_world = cast_hit.worldIntersection()
                    pos_local = cast_hit.localIntersection()

                    scene_obj = scene_obj_model_comp.scene_obj()
                    
                    scene_obj_ids.append(scene_obj.element_id())

                    pos_glob.append(pos_world)
                    pos_loc.append(pos_local)

        now = datetime.now()
        performed_cast_result = PerformedRayCastResult(now, 
                                                      scene_obj_ids, 
                                                      pos_glob, pos_loc)
        self._person.set_performed_ray_cast_result(performed_cast_result)

    @Slot()
    def _handle_hits_performed(self):
        performed_hits_result = self._person.performed_ray_cast_result()
        if performed_hits_result is None:
            return

        if self._last_shown_hits_results_timestamp < performed_hits_result.timestamp:
            self._last_shown_hits_results_timestamp = performed_hits_result.timestamp

            enable_points = self._attention_hit_points[:len(performed_hits_result.hits_global)]
            disable_points = self._attention_hit_points[len(performed_hits_result.hits_global):]
            for p, hit_world in zip(enable_points, performed_hits_result.hits_global):
                p.transform().setTranslation(hit_world)
                if not p.isEnabled():
                    p.setEnabled(True)
            for p in disable_points:
                if p.isEnabled():
                    p.setEnabled(False)

    def start_casting_attention_rays(self):
        # print(f'start_casting, {self._person=}')
        self._between_eyes_caster.set_casting_rays(True)
        self._left_eye_caster.set_casting_rays(True)
        self._right_eye_caster.set_casting_rays(True)
    
    def stop_casting_attention_rays(self):
        # print(f'stop_casting, {self._person=}')
        self._between_eyes_caster.set_casting_rays(False)
        self._left_eye_caster.set_casting_rays(False)
        self._right_eye_caster.set_casting_rays(False)

    def is_casting_attention_rays(self):
        return self._between_eyes_caster.is_casting_rays()

    @Slot(QVector3D)
    def _handle_camera_position_changed(self, pos:QVector3D):
        self._camera_transform.setTranslation(pos)
    
    @Slot(QQuaternion)
    def _handle_camera_rotation_changed(self, rotation:QQuaternion):
        self._camera_transform.setRotation(rotation)

    @Slot(QColor)
    def _handle_head_color_changed(self, color:QColor):
        self._head_mesh_material.setAmbient(color)
        for p in self._attention_hit_points:
            p.set_color(color)

    @Slot(ViewState)
    def update_view_state(self, state:ViewState):
        match(state):
            case ViewState.Plain:
                material_to_set = self._head_mesh_material
                materials_to_remove = self._errored_material, self._selected_material
            case ViewState.Errored: 
                if self._person.has_errored_state():
                    material_to_set = self._errored_material
                    materials_to_remove = self._selected_material, self._head_mesh_material
                else:
                    material_to_set = self._head_mesh_material
                    materials_to_remove = self._errored_material, self._selected_material
            case ViewState.Selected:
                if self._person.has_selected_state():
                    material_to_set = self._selected_material
                    materials_to_remove = self._errored_material, self._head_mesh_material
                else:
                    material_to_set = self._head_mesh_material
                    materials_to_remove = self._errored_material, self._selected_material
            case _:
                return
            
        if materials_to_remove[0] in self._head_entity.components():
            self._head_entity.removeComponent(materials_to_remove[0])
        if materials_to_remove[1] in self._head_entity.components():
            self._head_entity.removeComponent(materials_to_remove[1])
        if material_to_set not in self._head_entity.components():
            self._head_entity.addComponent(material_to_set)
    
    @Slot()
    def _handle_person_removed(self):
        self.setParent(None) #type:ignore
        self.deleteLater()


class CalibPoint(Qt3DCore.QEntity):
    position_changed = Signal(QVector3D)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._transform = Qt3DCore.QTransform()
        self._transform.translationChanged.connect(self._translation_changed)
        self.addComponent(self._transform)
        self._loader = Qt3DRender.QSceneLoader(self)
        self.addComponent(self._loader)
        self._loader.setSource(QUrl.fromLocalFile(src3d / 'calib_point.obj'))

    @Slot(QVector3D)
    def _translation_changed(self, pos:QVector3D):
        self.position_changed.emit(pos)

    def position(self) -> QVector3D:
        return self._transform.translation()
    
    def set_position(self, pos:QVector3D):
        self._transform.setTranslation(pos)


class AttentionScene3DService(QObject):
    scene_objs_ready = Signal()
    scene_objs_loading_started = Signal(QUrl)
    scene_objs_loading_in_progress = Signal()
    scene_objs_loading_failed = Signal(str)

    
    _update_view_state = Signal(ViewState)

    elements_selectable_by_picking_changed = Signal(bool)

    callibration_point_enabled_changed = Signal(bool)
    callibration_point_position_changed = Signal(QPointF)

    def __init__(self, render_window:RenderWindow) -> None:
        super().__init__()
        self._render_window:RenderWindow = render_window
        self._render_window.mouse_double_clicked.connect(self._observe_render_window_mouse_double_clicked)
        self._scene_3d = Qt3DCore.QEntity(self._render_window.root_entity())
        self._scene_tr = Qt3DCore.QTransform(self._scene_3d)
        self._scene_3d.addComponent(self._scene_tr)

        self._update_state_view_timer = QTimer(self)
        self._update_state_view_timer.setInterval(250)
        self._update_state_view_timer.setSingleShot(False)
        self._update_state_view_timer.timeout.connect(self._perform_view_state_update)
        self._view_state = ViewState.Plain
        self._update_state_view_timer.start()

        self._scene_objs_pick_layer = Qt3DRender.QLayer(self._scene_3d)
        self._scene_objs_pick_layer.setRecursive(True)

        self._scene_objs_root = Qt3DCore.QEntity(self._scene_3d)
        self._scene_objs_root_tr = Qt3DCore.QTransform(self._scene_objs_root)
        self._scene_objs_root.addComponent(self._scene_objs_root_tr)
        self._scene_objs_root.addComponent(self._scene_objs_pick_layer)

        self._scene_objs_loader:Qt3DRender.QSceneLoader|None = None

        self._person_entities_root = Qt3DCore.QEntity(self._scene_3d)
        self._person_entities_root.addComponent(Qt3DCore.QTransform(self._person_entities_root))
        self._person_entities_root.setObjectName('Root for all person entities')

        self._is_loading = False
        self._person_entities:list[Person3DModelEntity] = []
        self._scene_objs_components:list[SceneObj3dViewComponent] = []
        
        self._elements_selectable_by_picking = True
        self._calib_point = CalibPoint(self._scene_3d)
        self._calib_point.setEnabled(False)
        self._calib_point.enabledChanged.connect(self._calib_point_enabled_changed)
        self._screen_caster = Qt3DRender.QScreenRayCaster(self._scene_3d)
        self._screen_caster.setRunMode(Qt3DRender.QAbstractRayCaster.RunMode.SingleShot)
        self._screen_caster.addLayer(self._scene_objs_pick_layer)
        self._screen_caster.hitsChanged.connect(self._process_screen_hit)
        self._scene_3d.addComponent(self._screen_caster)

    def enable_callibration_point(self, enable:bool):
        print(f'enable_callibration_point({enable=})')
        self._calib_point.setEnabled(enable)
    
    def callibration_point_enabled(self) -> bool:
        return self._calib_point.isEnabled()
    
    @Slot(QVector3D)
    def _calib_point_position_changed(self, pos:QVector3D):
        self.callibration_point_position_changed.emit(pos)

    @Slot()
    def _process_screen_hit(self):
        hits = self._screen_caster.hits()
        if len(hits) > 0:
            if len(hits) > 1:
                closest_hit = min(*hits, key=lambda hit: hit.distance())
            else:
                closest_hit = hits[0]
            self._calib_point.set_position(closest_hit.worldIntersection())

    @Slot(QPoint)
    def _observe_render_window_mouse_double_clicked(self, pos:QPoint):
        print(f'_observe_render_window_mouse_clicked({pos=})')
        # self._screen_caster.setPosition()
        self._screen_caster.trigger(pos)

    @Slot(bool)
    def _calib_point_enabled_changed(self, is_enabled:bool):
        self.callibration_point_enabled_changed.emit(is_enabled)

    def set_elements_selectable_by_picking(self, val:bool):
        val = bool(val)

        for pe in self._person_entities:
            pe.set_selectable_by_picking(val)
        
        for so in self._scene_objs_components:
            so.set_selectable_by_picking(val)
        
        if val != self._elements_selectable_by_picking:
            self._elements_selectable_by_picking = val
            self.elements_selectable_by_picking_changed.emit(val)
    
    def elements_selectable_by_picking(self):
        return self._elements_selectable_by_picking
    
    def set_tracking(self, person:Person, is_tracking:bool):
        print(f'set_tracking({person=}, {is_tracking=})')
        def filter_person(ent:Person3DModelEntity) -> TypeGuard[Person3DModelEntity]:
            return ent._person.element_id() == person.element_id()
        person_ent = next(filter(filter_person, self._person_entities), None)
        print(f'{self._person_entities=}')
        if person_ent:
            if is_tracking:
                person_ent.start_casting_attention_rays()
            else:
                person_ent.stop_casting_attention_rays()

    @Slot()
    def _perform_view_state_update(self):
        states_chain ={
            ViewState.Plain:ViewState.Selected,
            ViewState.Selected: ViewState.Errored,
            ViewState.Errored:ViewState.Plain
        }
        self._view_state = states_chain[self._view_state]
        self._update_view_state.emit(self._view_state)

    def render_window(self):
        return self._render_window
    
    def loading_in_progress(self):
        return self._is_loading

    def create_workspace_for_person_model(self, person:Person):
        if not self._render_window:
            raise ValueError('render_window is not set yet')
        
        p = Person3DModelEntity(person, 
                            self._scene_objs_pick_layer, 
                            self._person_entities_root)
        p.set_selectable_by_picking(self._elements_selectable_by_picking)
        self._person_entities.append(p)
        self._update_view_state.connect(p.update_view_state)
    
    def initialize_from_objs_file(self, file_path:str|Path):
        if not self._render_window:
            raise ValueError('render_window is not set yet')
        if self._is_loading:
            # raise ValueError('Can not initialize while loading scene objs')
            self.scene_objs_loading_failed.emit('Previous scene objs loading is not complete yet')
            return
        self._remove_old_workspaces()
        self._remove_old_scene_objs()
        url = QUrl.fromLocalFile(str(Path(file_path).resolve()))
        self._make_new_scene_obj_loader(url)
        self._is_loading = True
        self.scene_objs_loading_started.emit(url)
    
    def scene_obj_names(self) -> list[str]:
        if not self._render_window:
            raise ValueError('render_window is not set yet')
        
        if self._scene_objs_loader is not None:
            return self._scene_objs_loader.entityNames()
        return []
    
    def attach_scene_obj_components(self, scene_objs:list[SceneObj]):
        if not self._render_window:
            raise ValueError('render_window is not set yet')
        
        if self._scene_objs_loader is None:
            raise RuntimeError('scene should be first initialized from model file')
        
        existing_entities = self.scene_obj_names()
        if not_found_scene_objs:=(set(existing_entities) - set([s_o.element_id() for s_o in scene_objs])):
            raise KeyError('Could not found scene obj entities, referenced by scene_obj_models:\n'+f"{list(not_found_scene_objs)}")
        
        for s_o in scene_objs:
            scene_obj_raw_name = s_o.element_id()
            scene_obj_entity = self._scene_objs_loader.entity(scene_obj_raw_name)
            model_component = SceneObj3dViewComponent(s_o)
            model_component.set_selectable_by_picking(self._elements_selectable_by_picking)
            self._update_view_state.connect(model_component.update_view_state)
            scene_obj_entity.addComponent(model_component)
            self._scene_objs_components.append(model_component)
    
    def reset_scene(self):
        if not self._render_window:
            raise ValueError('render_window is not set yet')
        
        self._remove_old_workspaces()
        self._remove_old_scene_objs()

    def _remove_old_workspaces(self):
        logging.info('removing old workspaces')
        ents = list(self._person_entities)
        self._person_entities.clear()
        for pe in ents:
            pe.setParent(None) # type: ignore
            pe.deleteLater()

    
    def _remove_old_scene_objs(self):
        logging.info('removing old scene_objs')
        print(f'before {self._scene_objs_components=}')
        for c in self._scene_objs_components:
            c.deleteLater()
        self._scene_objs_components.clear()

        print(f'after {self._scene_objs_components=}')
        print("DJNLKANSKJLDNL;")
        if self._scene_objs_loader is not None:
            logging.info('removing entities')
            print('removing_entitites')
            for ent in self._scene_objs_loader.entities():
                print(f'remove {ent=}')
                ent.setParent(None) # type: ignore
                ent.deleteLater()
            self._scene_objs_loader.setParent(None) # type: ignore
            self._scene_objs_loader.deleteLater()
            self._scene_objs_loader = None
        

    def _make_new_scene_obj_loader(self, src:QUrl):
        bind_entity = Qt3DCore.QEntity(self._scene_objs_root)
        bind_entity.addComponent(Qt3DCore.QTransform())
        self._scene_objs_loader = Qt3DRender.QSceneLoader(bind_entity)
        bind_entity.addComponent(self._scene_objs_loader)
        self._scene_objs_loader.statusChanged.connect(self._handle_scene_load_status_changed)
        self._scene_objs_loader.setSource(src)

    @Slot(Qt3DRender.QSceneLoader.Status)
    def _handle_scene_load_status_changed(self, status):
        print(self._scene_objs_loader, status)
        if self._scene_objs_loader:
            match self._scene_objs_loader.status():
                case Qt3DRender.QSceneLoader.Status.None_:
                    return
                case Qt3DRender.QSceneLoader.Status.Loading:
                    self.scene_objs_loading_in_progress.emit()
                case Qt3DRender.QSceneLoader.Status.Ready:
                    self._is_loading = False
                    QTimer.singleShot(0, self._emit_load_ready)
                case Qt3DRender.QSceneLoader.Status.Error:
                    self._is_loading = False
                    QTimer.singleShot(0, self._emit_load_failed,)
                    
    @Slot()
    def _emit_load_failed(self):
        if self._scene_objs_loader is None:
            return
        if status := self._scene_objs_loader.status():
            self.scene_objs_loading_failed.emit(str(status))
    
    @Slot()
    def _emit_load_ready(self):
        self.scene_objs_ready.emit()

