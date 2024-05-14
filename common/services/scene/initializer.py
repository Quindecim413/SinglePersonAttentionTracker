from dataclasses import dataclass
from logging import log
import logging
from pathlib import Path
from re import L
from PySide6.QtCore import QObject, Signal, Slot, QUrl, QTimer
from datetime import timedelta
from common.domain.models import AttentionSceneModel
from common.domain.interfaces import AttentionScene, Person
from common.dtos.descriptions import AttentionSceneDescription, SceneObjDescription
from common.services.scene.importers import AttentionProjectImporter, ProjectFromLocalArchiveImporter, ProjectModelDataImporter
from common.services.scene.project import AttentionProject
from common.services.scene.project_data import AttentionProjectData
from common.services.scene.repo import AttentionProjectsRepo, ProjectImportProcess
from common.services.scene.scene_3d import AttentionScene3DService
import traceback



def _initialize_scene_model(objs_names:list[str],
                            scene_description:AttentionSceneDescription):
    scene_model = AttentionSceneModel(objs_names)

    scene_obj_by_id = scene_model.scene_objs_by_id()
    for scene_obj_desc in scene_description.scene_objs:
        scene_obj = scene_obj_by_id.get(scene_obj_desc.id, None)
        if scene_obj is None:
            raise KeyError(f'Could not find SceneObjModel with id={scene_obj_desc.id}')
        scene_obj.set_element_name(scene_obj_desc.name)
        scene_obj.set_keep_attention_timedelta(scene_obj_desc.keep_attention_timedelta)
    
    for person_desc in scene_description.persons:
        scene_model.create_restored_person(person_desc)
    
    for rule_desc in scene_description.rules:
        scene_model.create_restored_attention_rule(rule_desc)

    return scene_model


class AttentionSceneInitializerService(QObject):
    scene_data_loading_started = Signal()
    scene_data_loading_failed = Signal(str)
    scene_data_loading_ready = Signal()

    scene_description_parsing_failed = Signal(str)
    
    attention_project_changed = Signal()

    has_initialized_project_changed = Signal(bool)

    def __init__(self,
                 attention_scene_3d_service:AttentionScene3DService,
                 scene_repo:AttentionProjectsRepo,
                 parent=None):
        super().__init__(parent)
        self._attention_scene_3d_service = attention_scene_3d_service
        self._scene_repo = scene_repo
        self._scene_repo.project_data_imported.connect(self._new_project_imported)

        self._attention_scene_3d_service.scene_objs_loading_started.connect(self._handle_scene_objs_loading_started)
        self._attention_scene_3d_service.scene_objs_loading_failed.connect(self._handle_scene_objs_loading_failed)
        self._attention_scene_3d_service.scene_objs_ready.connect(self._handle_scene_objs_ready)
        
        self._active_project_data:AttentionProjectData|None = None
        self._active_project: AttentionProject|None = None
        self._project_import_process:ProjectImportProcess|None = None

    @Slot(AttentionProjectData)
    def _new_project_imported(self, proj:AttentionProjectData):
        self.set_project_data(proj)
    
    def set_project_data(self, proj_data:AttentionProjectData|None):
        if self.project() is None and proj_data is None:
            return
        self._clear_current_project()                     
        if proj_data:
            self._active_project_data = proj_data
            self._active_project_data.removed.connect(self._project_removed)
            self._attention_scene_3d_service.initialize_from_objs_file(proj_data.storage().model_folder_path / proj_data.info.model_file_name)
    
    def reset_scene(self):
        self.set_project_data(self._active_project_data)

    def current_project(self)->AttentionProjectData|None:
        return self._active_project_data

    @Slot()
    def _project_removed(self):
        self._clear_current_project()

    def project(self) -> AttentionProject|None:
        return self._active_project
    
    def has_initialized_project(self):
        return self._active_project is not None
    
    def is_loading_scene_source(self,):
        return self._attention_scene_3d_service.loading_in_progress()

    def _clear_current_project(self):
        self._attention_scene_3d_service.reset_scene()

        if self._active_project_data is not None:
            self._active_project_data.setParent(None)
            self._active_project_data.disconnect(self)
            self._active_project_data = None
        
        if self._active_project is not None:
            self._active_project.setParent(None)
            self._active_project.disconnect(self)
            self._active_project = None
            self.attention_project_changed.emit()

    @Slot(QUrl)
    def _handle_scene_objs_loading_started(self, url):
        self.scene_data_loading_started.emit()
        logging.info(f'Start loading {url=}')
        print(f'Start loading {url=}')
    @Slot(str)
    def _handle_scene_objs_loading_failed(self, err_msg):
        self.scene_data_loading_failed.emit('Ошибка чтения файла модели окружения:\n'+err_msg)

    @Slot()
    def _handle_scene_objs_ready(self):
        obj_names = self._attention_scene_3d_service.scene_obj_names()
        try:
            if self._active_project_data is None:
                raise RuntimeError('_active_project_data cant be None')
            scene_model = _initialize_scene_model(obj_names,
                                                  self._active_project_data.description())
        except Exception as e:
            self._attention_scene_3d_service.reset_scene()
            self._scene_objs_file_path = None
            self.scene_description_parsing_failed.emit("Ошибка при анализе описания сцены:\n"+str(e)+'\n'+traceback.format_exc())
            return
        finally:
            self._description_to_parse = None

        try:
            self._attention_scene_3d_service.attach_scene_obj_components(scene_model.scene_objs())
            for person in scene_model.persons():
                self._attention_scene_3d_service.create_workspace_for_person_model(person)
        except Exception as e:
            self._clear_current_project()
            self.scene_data_loading_failed.emit('Ошибка инициализации объектов местности:\n'+str(e)+traceback.format_exc())
            return
        
        assert self._active_project_data is not None, '_active_project_data should not be None'

        self._active_project = AttentionProject(self._active_project_data, scene_model)
        scene_model.person_created.connect(self._observe_scene_person_created)
        
        self.scene_data_loading_ready.emit()
        self.attention_project_changed.emit()
    
    
    @Slot(Person)
    def _observe_scene_person_created(self, person:Person):
        self._attention_scene_3d_service.create_workspace_for_person_model(person)
