from abc import abstractmethod
from pathlib import Path
import zipfile
from PySide6.QtCore import QObject, Signal
from common.domain.obj_data import OBJData
from common.services.scene.project_data import AttentionProjectData
from common.services.scene.utils import ProjectInfo, ProjectStorageStructure


class BaseAttentionProjectExported(QObject):
    export_complete = Signal()
    export_failed = Signal(str)
    
    def __init__(self, project_data:AttentionProjectData):
        super().__init__()
        self.project_data = project_data

    def project_info(self) -> ProjectInfo:
        return self.project_data.info

    def export_project(self):
        self.do_export(self.project_data.storage())

    @abstractmethod
    def do_export(self, storage:ProjectStorageStructure):
        raise NotImplementedError()


class ProjectArchiverExporter(BaseAttentionProjectExported):
    def __init__(self, save_file_path:Path,
                 project_data:AttentionProjectData) -> None:
        super().__init__(project_data)
        if save_file_path.suffix != '.zip':
            save_file_path = save_file_path.parent / (save_file_path.name + '.zip')
        
        self.export_archive_path = save_file_path

    def do_export(self, storage: ProjectStorageStructure):        
        try:
            self.export_archive_path.parent.mkdir(exist_ok=True)
            with zipfile.ZipFile(self.export_archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                info = ProjectInfo.read_from_json(storage.info_file_path)
                model_path = storage.model_folder_path / info.model_file_name
                project_folder = storage.project_folder
                match(model_path.suffix):
                    case '.obj':
                        obj_data = OBJData(model_path)
                        obj_data.analize_includes()
                        mtls = obj_data.includes['mtl']
                        textures = obj_data.includes['textures']

                        arc_name = obj_data.obj_path.relative_to(project_folder)
                        zipf.write(obj_data.obj_path, arc_name)
                        
                        for mtl in mtls:
                            arc_name = mtl.relative_to(project_folder)
                            zipf.write(mtl, arc_name)
                        
                        for texture in textures:
                            arc_name = texture.relative_to(project_folder)
                            zipf.write(texture, arc_name)
                    case _:
                        raise ValueError('Unsupported model type, valid options: [".obj"]')
                zipf.write(storage.description_path, storage.description_file_name)
                zipf.write(storage.info_file_path, storage.info_file_name)
        except Exception as e:
            if self.export_archive_path.exists():
                self.export_archive_path.unlink()
            self.export_failed.emit(str(e))
            return
        self.export_complete.emit()
