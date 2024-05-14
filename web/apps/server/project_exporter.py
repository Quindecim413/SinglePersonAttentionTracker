from pathlib import Path
from typing import cast
from PySide6.QtCore import QObject, Slot, Signal
from common.services.scene.exporters import ProjectArchiverExporter
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.project import AttentionProject
from common.services.scene.utils import ProjectInfo
import os
import shutil


def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


class ActiveProjectExporter(QObject):
    active_project_archive_changed = Signal()
    active_project_archive_started = Signal(ProjectInfo)
    active_project_archive_complete = Signal(ProjectInfo)
    active_project_archive_failed = Signal(ProjectInfo, str)
    def __init__(self, 
                 projects_archives_dir:Path,
                 scene_initializer:AttentionSceneInitializerService,
                 ) -> None:
        super().__init__()
        self._projects_archives_dir = projects_archives_dir
        self._scene_initializer = scene_initializer
        self._scene_initializer.attention_project_changed.connect(self._observe_active_project_changed)
        self._active_project_archive:Path|None = None
        self._set_project(self._scene_initializer.project())
    
    def active_project_archive(self) -> Path|None:
        project = self._scene_initializer.project()
        if not project:
            return None
        
        archive_path = self._active_project_archive
        if archive_path and archive_path.exists():
            return archive_path
        return None
    
    def active_project_info(self) -> ProjectInfo|None:
        project = self._scene_initializer.project()
        if not project:
            return None
        return project.project_data().info

    @staticmethod
    def _create_path_for_active_project_archive(project:AttentionProject,
                                                base_dir:Path) -> Path:
        archive_path = base_dir / f'{project.project_data().project_id()}.zip'
        return archive_path

    @Slot()
    def _observe_active_project_changed(self):
        project = self._scene_initializer.project()
        self._set_project(project)
        
    def _set_project(self, project:AttentionProject|None):
        if project:
            archive_path = self._create_path_for_active_project_archive(project, self._projects_archives_dir)
            self._project_archiver = ProjectArchiverExporter(archive_path, project.project_data())
            self.active_project_archive_started.emit(self._project_archiver.project_info())
            self._project_archiver.export_complete.connect(self._archive_complete)
            self._project_archiver.export_failed.connect(self._archive_failed)
            self._project_archiver.export_project()

    def _update_last_project(self, new_project_archive:Path):
        self._active_project_archive = new_project_archive

    @Slot()
    def _archive_complete(self):
        archiver = cast(ProjectArchiverExporter, self._project_archiver)
        project_info = archiver.project_info()
        self._active_project_archive = archiver.export_archive_path
        self._project_archiver = None

        self.active_project_archive_complete.emit(project_info)
        self.active_project_archive_changed.emit()
    
    @Slot(str)
    def _archive_failed(self, reason:str):
        archiver = cast(ProjectArchiverExporter, self._project_archiver)
        project_info = archiver.project_info()
        self._active_project_archive = archiver.export_archive_path
        self._project_archiver = None

        self.active_project_archive_failed.emit(project_info, reason)
        self.active_project_archive_changed.emit()


    def _remove_active_project_archive(self):
        if self._active_project_archive:
            if self._active_project_archive.is_file():
                self._active_project_archive.unlink(missing_ok=True)
            else:
                shutil.rmtree(self._active_project_archive)
            self._active_project_archive = None
            self.active_project_archive_changed.emit()

    def close(self):
        self._remove_active_project_archive()