from abc import abstractmethod
from dataclasses import dataclass, replace, field
from datetime import datetime
import json
import logging
from re import S
from typing import cast
from uuid import uuid4
from dataclasses_json import DataClassJsonMixin
import shutil
from PySide6.QtCore import QObject, Signal, Slot

from pathlib import Path
from common.services.scene.importers import AttentionProjectImporter

from common.services.scene.project_data import AttentionProjectData
from common.services.scene.utils import ProjectInfo, ProjectStorageStructure, clear_directory_except_itself, init_project_storage_struct
from .config import MODEL_FOLDER_NAME, INFO_FILE_NAME, DESCRIPTION_FILE_NAME


def list_numeric_subfolders_names(dir:Path):
    return list(map(lambda d: int(d.name), filter(lambda d:d.is_dir() and d.name.isnumeric(), dir.iterdir())))


class ProjectImportProcess(QObject):
    started = Signal()
    complete = Signal()
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, 
                 repo:'AttentionProjectsRepo',
                 importer:AttentionProjectImporter
                 ) -> None:
        super().__init__()
        self.repo = repo
        self.importer = importer
        self.project_info:ProjectInfo = self.importer.get_project_info()
        storage = self.repo.create_new_storage_for_project()
        self.storage = storage
        self._cancelled = False
    
    def project_name(self):
        return self.project_info.project_name

    def _find_project(self, _id:str):
        return next(filter(lambda proj: proj.project_id()==_id, self.repo.projects_data()), None)

    def project_already_exists(self):
        return self._find_project(self.project_info.unique_id) is not None
    
    def run(self, override_if_exists=False):
        if self._cancelled:
            self.failed.emit('Import cancelled')
            return
        if self.project_already_exists() and not override_if_exists:
            self.failed.emit('project already exists')
            return
        try:
            self.importer.perform_import(self.storage)
            if self._cancelled:
                raise Exception('Import cancelled')
        except Exception as e:
            shutil.rmtree(self.storage.project_folder)
            self.failed.emit(str(e))
            return
        self.complete.emit()

    def cancel(self):
        self._cancelled = True
        if self.storage.project_folder.exists():
            shutil.rmtree(self.storage.project_folder)
            self.cancelled.emit()


class AttentionProjectsRepo(QObject):
    project_data_imported = Signal(AttentionProjectData)

    def __init__(self,
                 storage_dir:Path) -> None:
        super().__init__()
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cached_id2projects_data:dict[str, AttentionProjectData] = dict()

    def _scan_projects(self) -> list[AttentionProjectData]:
        projects:list[AttentionProjectData] = []
        for d in self.storage_dir.iterdir():
            meta_path = d / INFO_FILE_NAME
            desc_path = d / DESCRIPTION_FILE_NAME
            model_folder_path = d / MODEL_FOLDER_NAME
            if meta_path.exists() and meta_path.is_file() and\
                desc_path.exists() and desc_path.is_file() and\
                model_folder_path.exists() and model_folder_path.is_dir():
                try:
                    proj = AttentionProjectData(d)
                except Exception as e:
                    logging.warning(f'Failed to create attention project from directory {d}, ignoring it. Reason: {e}')
                    continue
                projects.append(proj)
        return projects

    def projects_data(self) -> list[AttentionProjectData]:
        for proj in self._scan_projects():
            if proj.project_id() not in self._cached_id2projects_data:
                self._cached_id2projects_data[proj.project_id()] = proj
        return list(self._cached_id2projects_data.values())

    def _get_free_project_folder(self):
        dirs = list_numeric_subfolders_names(self.storage_dir)
        print(f'{dirs=}')
        new_dir_name = str((max(dirs, default=0)+1))
        new_dir = self.storage_dir / new_dir_name
        return new_dir
    
    def create_new_storage_for_project(self) -> ProjectStorageStructure:
        new_proj_folder = self._get_free_project_folder()
        new_proj_folder.mkdir()
        storage = init_project_storage_struct(new_proj_folder)
        # storage.storage_removed
        return storage
    
    def remove_project_data(self, proj:AttentionProjectData):
        del self._cached_id2projects_data[proj.project_id()]
        shutil.rmtree(proj.storage().project_folder)
        proj.removed.emit()

    def create_import_project_process(self, 
                                      importer:AttentionProjectImporter):
        import_process = ProjectImportProcess(self, importer)
        import_process.complete.connect(self._project_imported)
        return import_process

    @Slot()
    def _project_imported(self):
        storage = cast(ProjectImportProcess, self.sender()).storage
        proj = AttentionProjectData(storage.project_folder)
        
        maybe_old_project = self._cached_id2projects_data.get(proj.project_id())
        if maybe_old_project:
            # папка с проектом с таким же project_id будет удалена, проект по факту создан с нуля
            self.remove_project_data(maybe_old_project)
        self.project_data_imported.emit(proj)

    def get_project_data_by_id(self, id:str) -> AttentionProjectData|None:
        return self._cached_id2projects_data.get(id)
    