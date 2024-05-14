from datetime import datetime
from pathlib import Path
from common.dtos.descriptions import AttentionSceneDescription
from common.services.scene.utils import ProjectInfo, init_project_storage_struct, read_scene_desc_from_file, write_scene_desc_to_file
from PySide6.QtCore import QObject, Signal
from .config import INFO_FILE_NAME, DESCRIPTION_FILE_NAME


class AttentionProjectData(QObject):
    removed = Signal()
    name_changed = Signal(str)
    def __init__(self,
                 folder:Path,
                 ) -> None:
        super().__init__()
        self.project_folder:Path = folder

        self._desc:AttentionSceneDescription = read_scene_desc_from_file(self.project_folder / DESCRIPTION_FILE_NAME)
        self.info = ProjectInfo.read_from_json(self.project_folder / INFO_FILE_NAME)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, AttentionProjectData):
            return False
        return self.project_folder == __value.project_folder

    def name(self) -> str:
        return self.info.project_name

    def set_name(self, name:str):
        old_name = self.info.project_name
        self.info.project_name = name
        if old_name != name:
            self.name_changed.emit(name)

    def project_id(self) -> str:
        return self.info.unique_id

    def creation_date(self) -> datetime:
        return self.info.creation_date

    def description(self) -> AttentionSceneDescription:
        return self._desc
    
    def storage(self):
        return init_project_storage_struct(self.project_folder)

    def set_description(self, desc:AttentionSceneDescription):
        self._desc = desc

    def save(self):
        write_scene_desc_to_file(self._desc, self.project_folder / DESCRIPTION_FILE_NAME)
        self.info.write_to_json(self.project_folder / INFO_FILE_NAME)