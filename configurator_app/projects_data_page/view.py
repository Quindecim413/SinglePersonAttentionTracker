from pathlib import Path
from typing import Callable
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QMessageBox, QFileDialog, QSizePolicy
from common.collections.projects import AvailableProjectDataItem
from common.services.scene.project_data import AttentionProjectData
from common.vms.project_loading import ProjectImportVM

from common.widgets.preview_expand import ItemViewFactory, PreviewExpandWidget, PreviewItem
from configurator_app.projects_data_page.preview_item import ProjectDataItemFactory
from .vm import ProjectsPageVM
from dependency_injector.wiring import inject, Provide


class ProjectsPage(QWidget):
    def __init__(self, 
                 vm:ProjectsPageVM,
                 project_import_vm:ProjectImportVM,
                 item_factory:ProjectDataItemFactory) -> None:
        super().__init__()
        self.vm = vm
        self.project_import_vm = project_import_vm
        self.preview_configure_widget = PreviewExpandWidget(self.vm.projects_data_collection(), item_factory)
        self.setMinimumSize(500, 500)
        self.setup_ui()
        self.layout().setContentsMargins(0,0,0,0)
        

        
        self.project_import_vm.scene_loading_ready.connect(self.handle_show_scene_loading_complete_msg)
        self.project_import_vm.scene_loading_failed.connect(self.handle_show_scene_loading_failed_msg)
        self.project_import_vm.scene_description_parsing_failed.connect(self.handle_show_scene_loading_failed_msg)
        self.project_import_vm.scene_import_ready.connect(self.handle_show_scene_importing_complete_msg)
        self.project_import_vm.scene_import_failed.connect(self.handle_show_scene_importing_failed_msg)
        self.project_import_vm.scene_import_cancelled.connect(self.handle_show_scene_importing_cancelled_msg)
        self.project_import_vm.request_aggrement_to_override_project.connect(self._request_project_override_by_import)

    def setup_ui(self):
        self.load_from_3d_model_btn = QPushButton("Создать новый проект")
        self.import_project_btn = QPushButton("Импортировать проект")
        self.load_from_3d_model_btn.clicked.connect(self._load_from_3d_model_clicked)
        self.import_project_btn.clicked.connect(self._import_project_clicked)

        controls_widget = QWidget()
        controls_vbox = QVBoxLayout()
        controls_vbox.addWidget(self.load_from_3d_model_btn)
        controls_vbox.addWidget(self.import_project_btn)
        controls_widget.setLayout(controls_vbox)

        self.preview_configure_widget.set_controls(controls_widget)
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_configure_widget)
        self.setLayout(vbox)

    @Slot(str)
    def _request_project_override_by_import(self, project_name:str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText(f"Проект {project_name} уже зарегистрирован в репозитории программы. Если продолжить импорт, его данные будут перезаписаны.""\nПродолжить?")
        msg_box.setWindowTitle("Данные проекта будут перезаписаны")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.No)
        ret = msg_box.exec()

        # Check the response
        if ret == QMessageBox.StandardButton.Ok:
            self.project_import_vm.accept_project_override()
        elif ret == QMessageBox.StandardButton.No:
            self.project_import_vm.reject_project_override()

    @Slot()
    def _load_from_3d_model_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Выберите файл формата OBJ",
                                                   "",  # Start at the current directory or specify a path
                                                   "OBJ Files (*.obj)")
        if file_name:
            self.project_import_vm.load_3d_scene_model_from_file(Path(file_name).resolve())

    @Slot()
    def _import_project_clicked(self):
        archive_file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Выберите архив с данными сцены",
                                                   "",  # Start at the current directory or specify a path
                                                   "Zip file (*.zip)")
        if not archive_file_name:
            return
        
        self.project_import_vm.import_scene_from_archive(Path(archive_file_name).resolve())

    @Slot()
    def handle_show_scene_loading_complete_msg(self):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Готово")
        self._mb.setText("Загрузка сцены прошла успешна")
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()
    
    @Slot(str)
    def handle_show_scene_loading_failed_msg(self, msg):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Critical)
        self._mb.setWindowTitle("Ошибка")
        self._mb.setText("Во время загрузки сцены произошла ошибка")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot()
    def handle_show_scene_importing_complete_msg(self):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Готово")
        self._mb.setText("Сцена успешно импортирована из архива")
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot(str)
    def handle_show_scene_importing_failed_msg(self, msg):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Critical)
        self._mb.setWindowTitle("Ошибка")
        self._mb.setText("Во время архива с данными сцены произошла ошибка")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot()
    def handle_show_scene_importing_cancelled_msg(self):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Импорт прерван")
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    
