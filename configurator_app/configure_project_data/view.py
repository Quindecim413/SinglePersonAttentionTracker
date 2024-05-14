from pathlib import Path
from PySide6.QtCore import Qt, Slot, Signal, QObject
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QPushButton, QFileDialog, QMessageBox
from common.services.scene.exporters import ProjectArchiverExporter
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.project_data import AttentionProjectData
from common.services.scene.repo import AttentionProjectsRepo


class ConfigureProjDataVM(QObject):
    show_scene_exporting_complete_msg = Signal(str)
    show_scene_exporting_failed_msg = Signal(str)

    project_name_changed = Signal(str)
    removed = Signal()
    project_saved = Signal()
    project_save_failed = Signal(str)

    is_current_scene_data_loaded_changed = Signal(bool)

    def __init__(self,
                 project_data:AttentionProjectData,
                 scene_initializer_service:AttentionSceneInitializerService,
                 projects_repo:AttentionProjectsRepo,
                 ) -> None:
        super().__init__()
        self._project_data = project_data
        self._project_data.name_changed.connect(self._project_name_changed)
        self.projects_repo = projects_repo
        self.scene_initializer_service = scene_initializer_service
        self.scene_initializer_service.attention_project_changed.connect(self._observe_attention_project_changed)
        self._project_archiver: ProjectArchiverExporter|None = None
        self._old_current_scene_data_loaded = self.is_current_scene_data_loaded()

    def export_scene_to_archive(self, archive_path:Path):
        pr = self.scene_initializer_service.project()
        if pr is None:
            self.show_scene_exporting_failed_msg.emit(f'Не выбран проект для экпорта')
            return
        self._project_archiver = ProjectArchiverExporter(archive_path, pr.project_data())
        self._project_archiver.export_complete.connect(self._archive_complete)
        self._project_archiver.export_complete.connect(self._archive_failed)
        self._project_archiver.export_project()

    def _remove_archiver(self):
        if self._project_archiver is not None:
            self._project_archiver.disconnect(self)
            self._project_archiver = None

    def save_project(self):
        pr = self.scene_initializer_service.project()
        if pr is None or pr.project_data().project_id() != self._project_data.project_id():
            self.project_save_failed.emit(f'Проект не загружен и не может быть сохранён')
            return
        try:
            pr.save()
        except Exception as e:
            self.project_save_failed.emit(str(e))
            return
        self.project_saved.emit()

    def clear_scene_description(self):
        return self.scene_initializer_service.reset_scene()

    def load_current_project(self):
        self.scene_initializer_service.set_project_data(self._project_data)

    def remove_project(self):
        self.projects_repo.remove_project_data(self._project_data)

    def project_id(self):
        return self._project_data.project_id()
    
    def project_name(self):
        return self._project_data.name()
    
    def set_project_name(self, name:str):
        assert isinstance(name, str)
        self._project_data.set_name(name)

    def created_date(self):
        return self._project_data.creation_date().isoformat()
    
    def project_directory(self):
        return str(self._project_data.storage().project_folder.resolve())
    
    def is_current_scene_data_loaded(self):
        current_proj = self.scene_initializer_service.project()
        if current_proj is None:
            return False
        return self._project_data.project_id() == current_proj.project_data().project_id()
    
    @Slot(str)
    def _project_name_changed(self, new_name:str):
        self.project_name_changed.emit(new_name)

    @Slot()
    def _observe_attention_project_changed(self):
        new_current_scene_data_loaded = self.is_current_scene_data_loaded()
        if new_current_scene_data_loaded != self._old_current_scene_data_loaded:
            self._old_current_scene_data_loaded = new_current_scene_data_loaded
            self.is_current_scene_data_loaded_changed.emit(new_current_scene_data_loaded)

    @Slot()
    def _archive_complete(self):
        if self._project_archiver:
            save_path = self._project_archiver.export_archive_path
            self.show_scene_exporting_complete_msg.emit(f'Данные сцены экспортированы в архив, {str(save_path)}')
        
        self._remove_archiver()

    @Slot(str)
    def _archive_failed(self, msg:str):
        if self._project_archiver:
            _n = '\n'
            self.show_scene_exporting_failed_msg.emit(f'При экспорте данных сцены произошла ошибка:{_n}{msg}')
        
        self._remove_archiver()

    @Slot(Path)
    def _handle_export_ready(self, save_path:Path):
        self.show_scene_exporting_complete_msg.emit(f'Данные сцены экспортированы в архив, {str(save_path)}')

    @Slot(str)
    def _handle_export_failed(self, msg):
        self.show_scene_exporting_failed_msg.emit(msg)


class ConfigureProjDataWidget(QWidget):
    def __init__(self,
                 vm:ConfigureProjDataVM) -> None:
        super().__init__()
        self.vm = vm

        self.vm.removed.connect(self._project_data_removed)
        self.vm.is_current_scene_data_loaded_changed.connect(self._observe_is_current_scene_data_loaded_changed)
        self.vm.show_scene_exporting_complete_msg.connect(self._handle_show_scene_exporting_complete_msg)
        self.vm.show_scene_exporting_failed_msg.connect(self._handle_show_scene_exporting_failed_msg)
        self.vm.project_save_failed.connect(self._handle_project_save_failed)
        self.vm.project_saved.connect(self._handle_project_saved)
        self.setup_ui()

        self._set_view_with_loaded_state(self.vm.is_current_scene_data_loaded())
        
    @Slot(bool)
    def _observe_is_current_scene_data_loaded_changed(self, is_current_selected):
        self._set_view_with_loaded_state(is_current_selected)

    def _set_view_with_loaded_state(self, is_current_selected:bool):
        self._load_btn.setEnabled(not is_current_selected)
        self._save_btn.setEnabled(is_current_selected)
        self._reset_description_of_scene_btn.setEnabled(is_current_selected)
        self._export_project_btn.setEnabled(is_current_selected)
        
        if is_current_selected:    
            self._load_btn.setText('Загружено')
        else:
            if self._load_btn.text() != 'Загрузить':
                self._load_btn.setText('Загрузить')

    def setup_ui(self):
        self._id_lbl = QLabel(self.vm.project_id())
        self._name_edit = QLineEdit(self.vm.project_name())
        self._name_edit.textChanged.connect(self._name_input_text_changed)
        self._name_edit.returnPressed.connect(self._name_input_text_entered)
        self._time_created_lbl = QLabel(self.vm.created_date())
        self._store_directory = QLineEdit()
        self._store_directory.setReadOnly(True)
        self._store_directory.setText(self.vm.project_directory())


        self._remove_btn = QPushButton('Удалить')
        self._load_btn = QPushButton('Загрузить')
        self._save_btn = QPushButton('Сохранить')    
        self._reset_description_of_scene_btn = QPushButton("Отменить изменения")
        self._export_project_btn = QPushButton("Экспортировать")
        
        self._save_btn.clicked.connect(self._save_btn_clicked)
        self._reset_description_of_scene_btn.clicked.connect(self._reset_description_of_scene_clicked)
        self._export_project_btn.clicked.connect(self._export_project_clicked)

        self._load_btn.clicked.connect(self._load_clicked)
        self._remove_btn.clicked.connect(self._remove_clicked)

        vbox = QVBoxLayout()
        buttons_grid = QGridLayout()
        buttons_grid.addWidget(self._load_btn, 0, 0, 1, 3)
        buttons_grid.addWidget(self._remove_btn, 0, 3, 1, 3)
        buttons_grid.addWidget(self._reset_description_of_scene_btn, 1, 0, 1, 2)
        buttons_grid.addWidget(self._save_btn, 1, 2, 1, 2)
        buttons_grid.addWidget(self._export_project_btn, 1, 4, 1, 2)
        vbox.addLayout(buttons_grid)

        grid = QGridLayout()
        grid.addWidget(QLabel('Сцена #'), 0, 0)
        grid.addWidget(self._id_lbl, 0, 1)
        grid.addWidget(QLabel('Название'), 1, 1)
        grid.addWidget(self._name_edit, 1, 1)

        grid.addWidget(QLabel('Дата создания'), 2, 0)
        grid.addWidget(self._time_created_lbl, 2, 1)
        grid.addWidget(QLabel('Путь'), 3, 0)
        grid.addWidget(self._store_directory, 4, 0, 1, 2)

        vbox.addLayout(grid)

        self.setLayout(vbox)

    @Slot()
    def _save_btn_clicked(self):
        self.vm.save_project()

    @Slot()
    def _export_project_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Укажите файл для сохранения архива данных сцены",
            "",  # Start directory
            "ZIP Files (*.zip);;All Files (*)",
        )

        if not file_name:
            return
        if not file_name.endswith('.zip'):
            file_name += '.zip'
        
        self.vm.export_scene_to_archive(Path(file_name).resolve())

    @Slot()
    def _project_data_removed(self):
        self.setEnabled(False)

    @Slot()
    def _load_clicked(self):
        self.vm.load_current_project()

    @Slot()
    def _reset_description_of_scene_clicked(self):
        self.vm.clear_scene_description()

    @Slot()
    def _remove_clicked(self):
        self.vm.remove_project()
    
    @Slot()
    def _name_input_text_entered(self):
        self.vm.set_project_name(self._name_edit.text())
    
    @Slot(str)
    def _name_input_text_changed(self, text):
        self.vm.set_project_name(text)

    @Slot(str)
    def _name_changed(self, name):
        self._name_edit.setText(name)

    @Slot()
    def _handle_project_saved(self):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Готово")
        self._mb.setText("Проект сохранен")
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()
    
    @Slot(str)
    def _handle_project_save_failed(self, msg):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Critical)
        self._mb.setWindowTitle("Ошибка")
        self._mb.setText("Во время сохранения проекта произошла ошибка")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot(str)
    def _handle_show_scene_exporting_complete_msg(self, msg):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Готово")
        self._mb.setText("Сцена успешно экспортирована в архив")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot(str)
    def _handle_show_scene_exporting_failed_msg(self, msg):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Critical)
        self._mb.setWindowTitle("Ошибка")
        self._mb.setText("Во время экспорта сцены в архив произошла ошибка")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()
