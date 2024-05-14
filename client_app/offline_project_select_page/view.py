from pathlib import Path
from PySide6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLabel, QMessageBox, QScrollArea, QFileDialog, QHBoxLayout, QToolButton 
from PySide6.QtCore import QObject, Slot, Signal
from common.widgets.project_data_select.widget import ProjectDataSelectionWidget
from client_app.services.processing_mode_selector import ProcessingModeSelector
from common.vms.project_loading import ProjectImportVM


class OfflineSelectProjectPageVM(QObject):
    project_selectable_changed = Signal(bool)

    def __init__(self,
                 processing_mode_selector:ProcessingModeSelector) -> None:
        super().__init__()
        self._processing_mode_selector = processing_mode_selector
        self._processing_mode_selector.running_mode_changed.connect(self._observe_running_mode_changed)

    @Slot(ProcessingModeSelector.RunningMode)
    def _observe_running_mode_changed(self, running_mode:ProcessingModeSelector.RunningMode):
        self.project_selectable_changed.emit(self.project_selectable())

    def project_selectable(self) -> bool:
        return self._processing_mode_selector.running_mode() == ProcessingModeSelector.RunningMode.Offline


class OfflineSelectProjectPage(QWidget):
    def __init__(self, 
                 vm:OfflineSelectProjectPageVM,
                 project_import_vm:ProjectImportVM,
                 select_project_data_widget:ProjectDataSelectionWidget) -> None:
        super().__init__()
        self.vm = vm
        self.vm.project_selectable_changed.connect(self._observe_project_selectable_changed)
        self.project_import_vm = project_import_vm
        self._select_project_data_widget = select_project_data_widget
        self.setup_ui()
        self.project_import_vm.request_aggrement_to_override_project.connect(self._request_project_override_by_import)
        self.project_import_vm.scene_loading_ready.connect(self._handle_scene_loading_ready)
        self.project_import_vm.scene_loading_failed.connect(self._handle_scene_loading_failed)
        self.project_import_vm.scene_description_parsing_failed.connect(self._handle_scene_description_loading_failed)
        
        self.project_import_vm.scene_import_ready.connect(self._handle_import_ready)
        self.project_import_vm.scene_import_failed.connect(self._handle_import_failed)
        self.project_import_vm.scene_import_cancelled.connect(self._handle_cancelled)

        self._set_project_selectable(self.vm.project_selectable())

    def setup_ui(self):
        self._import_project_btn = QToolButton()
        self._import_project_btn.setText('...')
        self._import_project_btn.clicked.connect(self._import_project_clicked)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Импортировать проект'))
        hbox.addWidget(self._import_project_btn)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self._select_project_data_widget)
        self.scroll_area.setWidgetResizable(True)
        vbox.addWidget(self.scroll_area)
        self.setLayout(vbox)

    @Slot(bool)
    def _observe_project_selectable_changed(self, is_selectable:bool):
        self._set_project_selectable(is_selectable)

    def _set_project_selectable(self, is_selectable:bool):
        print(f'_set_project_selectable(self, {is_selectable=}:bool)')
        self.setEnabled(is_selectable)

    @Slot()
    def _import_project_clicked(self):
        archive_file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Выберите архив с данными сцены",
                                                   "",  # Start at the current directory or specify a path
                                                   "Zip file (*.zip)")
        if not archive_file_name:
            return
        
        self.project_import_vm.import_scene_from_archive(Path(archive_file_name).resolve())

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

    @Slot(str)
    def _handle_scene_description_loading_failed(self, msg):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Critical)
        self._mb.setWindowTitle("Ошибка")
        self._mb.setText("Во время загрузки сцены произошла ошибка")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot()
    def _handle_scene_loading_ready(self):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Готово")
        self._mb.setText("Загрузка сцены прошла успешна")
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()
    
    @Slot(str)
    def _handle_scene_loading_failed(self, msg):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Critical)
        self._mb.setWindowTitle("Ошибка")
        self._mb.setText("Во время загрузки сцены произошла ошибка")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot()
    def _handle_import_ready(self):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Готово")
        self._mb.setText("Сцена успешно импортирована из архива")
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot(str)
    def _handle_import_failed(self, msg:str):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Critical)
        self._mb.setWindowTitle("Ошибка")
        self._mb.setText("Во время архива с данными сцены произошла ошибка")
        self._mb.setInformativeText(msg)
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()

    @Slot()
    def _handle_cancelled(self):
        self._mb = QMessageBox(self)
        self._mb.setIcon(QMessageBox.Icon.Information)
        self._mb.setWindowTitle("Импорт прерван")
        self._mb.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._mb.exec()