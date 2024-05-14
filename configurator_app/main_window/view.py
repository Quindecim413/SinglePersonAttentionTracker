from typing import Callable
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QMainWindow, QSizePolicy, QLabel
from pathlib import Path
from common.domain.interfaces import AttentionScene
from common.utils import clear_layout
from common.widgets.render_widget import RenderWidget
from common.windows.scene import SceneWindow

from configurator_app.main_window.vm import ConfigureWindowVM
from configurator_app.persons_page.view import ConfigurePersonsPage
from configurator_app.persons_page.vm import ConfigurePersonsPageVM
from configurator_app.projects_data_page.view import ProjectsPage
from configurator_app.rules_page.vm import ConfigureRulesPageVM
from configurator_app.scene_objs_page.vm import ConfigureSceneObjsPageVM
from ..rules_page.view import ConfigureRulesPage
from ..scene_objs_page.view import ConfigureSceneObjsPage
from .ui import Ui_MainWindow
from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory


class ConfigureWindow(QMainWindow, Ui_MainWindow):
    @inject
    def __init__(self, 
                 vm:ConfigureWindowVM,
                 scene_window:SceneWindow,
                 projects_page:ProjectsPage,
                 configure_persons_page_factory:Factory[ConfigurePersonsPage],
                 configure_scene_objs_page_factory:Factory[ConfigureSceneObjsPage],
                 configure_attention_rules_page_factory:Factory[ConfigureRulesPage]
                 ):
        super().__init__()
        self.scene_window = scene_window
        self.setupUi(self)
        self.scene_window.bring_to_front()
        w = QLabel('hah')
        # background-color: rgb(170, 170, 255);
        # projects_page.setStyleSheet('QWidget{background-color: rgb(170, 170, 255);}')
        w.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        projects_page.setContentsMargins(0,0,0,0)
        self.page_projects_content.layout().addWidget(projects_page)


        self.configure_persons_page_factory = configure_persons_page_factory
        self.configure_scene_objs_page_factory = configure_scene_objs_page_factory
        self.configure_attention_rules_page_factory = configure_attention_rules_page_factory

        self.vm = vm
    
        self.vm.attention_scene_editable_changed.connect(self.handle_attention_scene_elements_editable_changed)
        self.show_scene_btn.clicked.connect(self._show_scene_btn_clicked)

        self.configure_projects_btn.clicked.connect(self._configure_projects_btn_clicked)
        self.configure_persons_btn.clicked.connect(self._configure_persons_btn_clicked)
        self.configure_scene_objs_btn.clicked.connect(self._configure_scene_objs_btn_clicked)
        self.configure_rules_btn.clicked.connect(self._configure_rules_btn_clicked)

        self._set_projects_page()
        
    @Slot()
    def _show_scene_btn_clicked(self):
        self.scene_window.bring_to_front()

    @Slot()
    def _configure_projects_btn_clicked(self):
        self._set_projects_page()

    @Slot()
    def _configure_scene_objs_btn_clicked(self):
        self._set_scene_objs_page()

    @Slot()
    def _configure_persons_btn_clicked(self):
        self._set_persons_page()

    @Slot()
    def _configure_rules_btn_clicked(self):
        self._set_rules_page()

    @Slot()
    def handle_attention_scene_elements_editable_changed(self):
        self.set_attention_scene_editable(self.vm.attention_scene_elements_editable())

    def set_attention_scene_editable(self, editable:bool):
        clear_layout(self.page_persons_content.layout())
        clear_layout(self.page_scene_objs_content.layout())
        clear_layout(self.page_rules_content.layout())
        if not editable:
            self._set_projects_page()
            self.configure_persons_btn.setEnabled(False)
            self.configure_scene_objs_btn.setEnabled(False)
            self.configure_rules_btn.setEnabled(False)
        if editable:
            self.configure_persons_btn.setEnabled(True)
            self.configure_scene_objs_btn.setEnabled(True)
            self.configure_rules_btn.setEnabled(True)
            self.page_persons_content.layout().addWidget(self.configure_persons_page_factory(self.vm.persons_window_vm()))
            self.page_scene_objs_content.layout().addWidget(self.configure_scene_objs_page_factory(self.vm.scene_objs_window_vm()))
            self.page_rules_content.layout().addWidget(self.configure_attention_rules_page_factory(self.vm.rules_window_vm()))

    def _set_projects_page(self):
        self.stackedWidget.setCurrentWidget(self.page_projects)
        self.configure_projects_btn.setChecked(True)
        self.configure_persons_btn.setChecked(False)
        self.configure_scene_objs_btn.setChecked(False)
        self.configure_rules_btn.setChecked(False)

    def _set_persons_page(self):
        self.stackedWidget.setCurrentWidget(self.page_persons)
        self.configure_projects_btn.setChecked(False)
        self.configure_persons_btn.setChecked(True)
        self.configure_scene_objs_btn.setChecked(False)
        self.configure_rules_btn.setChecked(False)

    def _set_scene_objs_page(self):
        self.stackedWidget.setCurrentWidget(self.page_scene_objs)
        self.configure_projects_btn.setChecked(False)
        self.configure_persons_btn.setChecked(False)
        self.configure_scene_objs_btn.setChecked(True)
        self.configure_rules_btn.setChecked(False)

    def _set_rules_page(self):
        self.stackedWidget.setCurrentWidget(self.page_rules)
        self.configure_projects_btn.setChecked(False)
        self.configure_persons_btn.setChecked(False)
        self.configure_scene_objs_btn.setChecked(False)
        self.configure_rules_btn.setChecked(True)
    
    def closeEvent(self, event):
        self.scene_window.close()