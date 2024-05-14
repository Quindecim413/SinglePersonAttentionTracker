from ast import Try
from pathlib import Path
from re import L
from PySide6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLabel, QMessageBox, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import QObject, Slot, Signal
from client_app.services.processing_mode_selector import ProcessingModeSelector
from common.services.active_person import ActivePersonSelector
from common.services.scene.importers import AttentionProjectImporter, ProjectFromLocalArchiveImporter, ProjectModelDataImporter
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.repo import AttentionProjectsRepo, ProjectImportProcess
from common.services.scene.utils import ProjectInfo


class ProjectImportVM(QWidget):
    scene_loading_ready = Signal()
    scene_loading_failed = Signal(str)
    scene_description_parsing_failed = Signal(str)

    scene_import_ready = Signal()
    scene_import_failed = Signal(str)
    scene_import_cancelled = Signal()

    request_aggrement_to_override_project = Signal(str)

    def __init__(self, 
                 scene_initializer:AttentionSceneInitializerService,
                 projects_repo:AttentionProjectsRepo) -> None:
        super().__init__()
        self._scene_initializer = scene_initializer
        self._projects_repo = projects_repo

        self._scene_initializer.scene_data_loading_failed.connect(self._handle_scene_loading_failed)
        self._scene_initializer.scene_data_loading_ready.connect(self._handle_scene_loading_ready)
        self._scene_initializer.scene_description_parsing_failed.connect(self._handle_scene_description_parsing_failed)

        self._import_process:ProjectImportProcess|None = None

    @Slot(str)
    def _observe_importing_about_to_override_data(self, project_name:str):
        self.request_aggrement_to_override_project.emit(project_name)

    @Slot()
    def _handle_scene_loading_ready(self):
        self.scene_loading_ready.emit()

    @Slot(str)
    def _handle_scene_loading_failed(self, msg:str):
        self.scene_loading_failed.emit(msg)

    @Slot(str)
    def _handle_scene_description_parsing_failed(self, msg):
        self.scene_description_parsing_failed.emit(msg)

    @Slot(str)
    def _handle_import_failed(self, msg:str):
        self._clear_import_process()
        self.scene_import_failed.emit(msg)

    @Slot()
    def _handle_import_ready(self):
        self._clear_import_process()
        self.scene_import_ready.emit()

    @Slot()
    def _handle_import_cancelled(self):
        self._clear_import_process()
        self.scene_import_cancelled.emit()

    def import_scene_from_archive(self, path:Path):
        if self._check_import_process_running():
            self._show_import_process_running_error()
            return
        model_data_importer = ProjectFromLocalArchiveImporter(path)
        self._set_new_importer(model_data_importer)

    def accept_project_override(self):
        if self._import_process is not None:
            self._import_process.run(True)

    def reject_project_override(self):
        if self._import_process is not None:
            self._import_process.cancel()

    def load_3d_scene_model_from_file(self, filename:Path):
        if self._check_import_process_running():
            self._show_import_process_running_error()
            return
        
        archive_importer = ProjectModelDataImporter(filename)
        self._set_new_importer(archive_importer)

    def _check_import_process_running(self):
        return self._import_process is not None
    
    def _show_import_process_running_error(self):
        if (import_process:=self._import_process) is not None:
            info = import_process.importer.get_project_info()
            self.scene_import_failed.emit(f'Импорт проекта {info.project_name}(#{info.unique_id}) не завершен')

    def _set_new_importer(self, project_importer:AttentionProjectImporter):
        if self._import_process is not None:
            raise RuntimeError(f'{self._import_process} still running')
        importer_process = self._projects_repo.create_import_project_process(project_importer)
        self._import_process = importer_process
        self._bind_import_process_signals(self._import_process)

        if self._import_process.project_already_exists():
            self.request_aggrement_to_override_project.emit()
            return
        self._import_process.run()

    def _bind_import_process_signals(self, import_process:ProjectImportProcess):
        import_process.failed.connect(self._handle_import_failed)
        import_process.complete.connect(self._handle_import_ready)
        import_process.cancelled.connect(self._handle_import_cancelled)

    def _clear_import_process(self,):
        self._import_process = None