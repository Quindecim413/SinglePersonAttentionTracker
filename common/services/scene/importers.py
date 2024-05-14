from abc import abstractmethod
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory, tempdir
import zipfile
from PySide6.QtCore import QObject, Signal
from common.dtos.descriptions import AttentionSceneDescription
from common.domain.obj_data import OBJData
from common.services.scene.config import INFO_FILE_NAME
from common.services.scene.utils import ProjectInfo, ProjectStorageStructure, clear_directory_except_itself, copy_directory_contents, copy_obj_file_data_to_folder, read_scene_desc_from_file, write_scene_desc_to_file


class AttentionProjectImporter(QObject):
    import_complete = Signal()
    import_failed = Signal(str)
    
    @abstractmethod
    def get_project_info(self) -> ProjectInfo:
        raise NotImplementedError()

    @abstractmethod
    def perform_import(self, storage:ProjectStorageStructure):
        raise NotImplementedError()


class ProjectModelDataImporter(AttentionProjectImporter):
    def __init__(self, model_path:Path) -> None:
        super().__init__()
        self.model_path = model_path
        self._proj_info:ProjectInfo|None = None
    
    def get_project_info(self) -> ProjectInfo:
        if self._proj_info is None:
            self._proj_info = ProjectInfo(project_name=f"Unnamed project from {self.model_path.name}",
                               model_file_name=self.model_path.name)
        return self._proj_info

    def perform_import(self, storage: ProjectStorageStructure):
        if self.model_path.suffix != '.obj':
            raise ValueError('Unsupported model type, valid options: [".obj"]')
        
        storage.project_folder.mkdir(exist_ok=True)
        storage.model_folder_path.mkdir()
        match(self.model_path.suffix):
            case '.obj':
                obj_data = OBJData(self.model_path)
                obj_data.analize_includes()
                copy_obj_file_data_to_folder(obj_data, storage.model_folder_path)
            case _:
                raise ValueError('Invalid file type')
        
        self.get_project_info().write_to_json(storage.info_file_path)
        write_scene_desc_to_file(AttentionSceneDescription([], [], []), 
                                    storage.description_path)


class ProjectFromLocalArchiveImporter(AttentionProjectImporter):
    def __init__(self, project_archive_path:Path,
                 info_file_name=INFO_FILE_NAME) -> None:
        super().__init__()
        self.project_archive_path = project_archive_path
        self.info_file_name = info_file_name

    def get_project_info(self) -> ProjectInfo:
        with zipfile.ZipFile(self.project_archive_path, 'r') as zipf:
            return ProjectInfo.from_json(zipf.open(self.info_file_name).read())

    def perform_import(self, storage: ProjectStorageStructure):
        with TemporaryDirectory() as d:
            tmp_dir_path = Path(d)
            try:
                self._unzip_to_folder_and_verify_content(self.project_archive_path, storage)
                clear_directory_except_itself(storage.project_folder)
                copy_directory_contents(tmp_dir_path, storage.project_folder)
            except Exception as e:
                self.import_failed.emit(str(e))
                return
            self.import_complete.emit()
    
    @staticmethod
    def _unzip_to_folder_and_verify_content(project_archive_path:Path, 
                                            storage:ProjectStorageStructure):
        with zipfile.ZipFile(project_archive_path, 'r') as zipf:
            # Extract all the contents of the zip file into the directory
            zipf.extractall(storage.project_folder)
        if not storage.description_path.exists():
            raise ValueError('description file not found')
        if not storage.info_file_path.exists():
            raise ValueError('project meta file not found')
        if not storage.model_folder_path.exists():
            raise ValueError('model data folder not found')
        meta = ProjectInfo.read_from_json(storage.description_path)
        # verity that files in valid format

        try:
            model_file_path = storage.model_folder_path / meta.model_file_name
            match(model_file_path.suffix):
                case '.obj':
                    obj_data = OBJData(model_file_path)
                    obj_data.analize_includes()
                case _:
                    raise ValueError('Unsupported model type, valid files: [".obj"]')
        except Exception as e:
            raise Exception(f'Error when analizing model file: {e}')
