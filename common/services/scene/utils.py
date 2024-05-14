from datetime import datetime
import json
from pathlib import Path
import shutil
from uuid import uuid4
from dataclasses import dataclass, field
from common.dtos.descriptions import AttentionSceneDescription, AttentionSceneDescriptionAdapter
from common.domain.obj_data import OBJData
from dataclasses_json import DataClassJsonMixin
from .config import MODEL_FOLDER_NAME, INFO_FILE_NAME, DESCRIPTION_FILE_NAME


def init_project_storage_struct(project_folder:Path):
    return ProjectStorageStructure(
        project_folder=project_folder,
        info_file_name=INFO_FILE_NAME,
        description_file_name=DESCRIPTION_FILE_NAME,
        model_folder_name=MODEL_FOLDER_NAME,
    )


@dataclass
class ProjectInfo(DataClassJsonMixin):
    project_name:str
    model_file_name:str
    creation_date:datetime = field(default_factory=datetime.now)
    unique_id:str = field(default_factory=lambda:str(uuid4()))

    def write_to_json(self, path:Path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json(ensure_ascii=False, indent=4))
    @staticmethod
    def read_from_json(path:Path):
        with open(path, 'r', encoding='utf-8') as f:
            return ProjectInfo.from_json(f.read())
        

class ProjectStorageStructure:
    def __init__(self,
                 project_folder:Path,
                 info_file_name:str,
                 description_file_name:str,
                 model_folder_name:str):
        self.project_folder = project_folder
        self.info_file_name = info_file_name
        self.description_file_name = description_file_name
        self.model_folder_name = model_folder_name

    def remove(self):
        shutil.rmtree(self.project_folder)

    @property
    def model_folder_path(self):
        return self.project_folder / self.model_folder_name

    @property
    def description_path(self):
        return self.project_folder / self.description_file_name

    @property
    def info_file_path(self):
        return self.project_folder / self.info_file_name
    

def copy_obj_file_data_to_folder(obj_data:OBJData, folder:Path):
    if not (folder.is_dir()):
        raise ValueError('folder is expected to be a directory')
    
    mtls = obj_data.includes['mtl']
    textures = obj_data.includes['textures']

    obj_dir = obj_data.obj_path.parent

    shutil.copy(obj_data.obj_path, folder / obj_data.obj_path.name)
    
    for mtl in mtls:
        arc_name = mtl.relative_to(obj_dir)
        dst = folder / arc_name
        shutil.copy(mtl, dst)
    
    for texture in textures:
        arc_name = texture.relative_to(obj_dir)
        dst = folder / arc_name
        shutil.copy(texture, dst)


def read_scene_desc_from_file(path:Path) -> AttentionSceneDescription:
    with open(path, 'r', encoding='utf-8') as f:
        return AttentionSceneDescriptionAdapter.validate_json(f.read())


def write_scene_desc_to_file(scene_desc:AttentionSceneDescription, 
                        path:Path):
    with open(path, 'wb') as f:
        json_bytes = AttentionSceneDescriptionAdapter.dump_json(scene_desc, indent=4)
        f.write(json_bytes)


import os
import shutil

def clear_directory_except_itself(dir_path:Path):
    for item_name in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item_name)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

# # Usage example:
# directory_to_clear = '/path/to/your/directory'
# clear_directory_except_itself(directory_to_clear)


import os
import shutil

def copy_directory_contents(src_dir:Path, dst_dir:Path):
    # Ensure the source directory exists
    if not src_dir.exists():
        raise ValueError("Source directory does not exist")

    # Ensure the destination directory exists, if not, create it
    if not dst_dir.exists():
        dst_dir.mkdir()

    # Iterate over all the files and directories in the source directory
    for item in os.listdir(src_dir):
        src_item = src_dir / item
        dst_item = dst_dir / item

        # Copy each item to the destination directory
        if src_item.is_dir():
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
        else:
            shutil.copy2(src_item, dst_item)

# # Example usage:
# source_directory = '/path/to/source/directory'
# destination_directory = '/path/to/destination/directory'
# copy_directory_contents(source_directory, destination_directory)
