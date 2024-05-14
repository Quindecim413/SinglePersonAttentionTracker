from re import L
from PySide6.QtCore import Qt, QObject, Slot, Signal
from PySide6.QtGui import QCloseEvent, QMouseEvent, QActionGroup
from PySide6.QtWidgets import  QWidget, QFrame, QSizePolicy,\
    QSplitter, QScrollArea, QVBoxLayout, QMainWindow, QLabel, QButtonGroup
from client_app.main.vm import ClientMainWindowVM
from client_app.services.processing_mode_selector import ProcessingModeSelector
from common.services.scene.initializer import AttentionSceneInitializerService

from common.windows.scene import SceneWindow

from .ui import Ui_MainWindow
from common.utils import clear_layout


# class PageContentWidget(QScrollArea):
#     def __init__(self, content_widget:QWidget) -> None:
#         super().__init__()
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
#         self.setWidgetResizable(True)
#         self.setWidget(content_widget)


class ClientMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, 
                 vm:ClientMainWindowVM,
                 camera_page:QWidget,
                 networking_page:QWidget,
                 callibration_page:QWidget,
                 offline_project_select_page:QWidget,
                 person_select_page:QWidget,
                 tracking_page:QWidget,
                 scene_window:SceneWindow,
                 ) -> None:
        super().__init__()
        self.setupUi(self)
        self.vm = vm
        self.vm.can_show_networking_page_changed.connect(self._observe_can_show_networking_page)
        self.vm.can_show_offline_project_select_page_changed.connect(self._observe_can_show_offline_project_select_page)
        self.vm.can_show_person_select_page_changed.connect(self._observe_can_show_person_select_page_changed)
        self.vm.focus_networking_page.connect(self.navigate_networking_page)
        self.vm.focus_offline_page.connect(self.navigate_offline_project_select_page)
        self.page_camera_content.layout().addWidget((camera_page))
        self.page_network_content.layout().addWidget((networking_page))
        self.page_callibration_content.layout().addWidget(callibration_page)
        self.page_offline_project_select_content.layout().addWidget(offline_project_select_page)
        self.page_select_person_content.layout().addWidget(person_select_page)
        self.page_tracking_content.layout().addWidget((tracking_page))

        self.scene_window = scene_window
        self.scene_window.show()
        self.camera_page_btn.clicked.connect(self._handle_camera_page_btn_clicked)
        self.networking_page_btn.clicked.connect(self._handle_networking_page_btn_clicked)
        self.tracking_page_btn.clicked.connect(self._handle_tracking_page_btn_clicked)
        self.offine_project_select_page_btn.clicked.connect(self._handle_offline_project_select_page_btn_clicked)
        self.person_select_page_btn.clicked.connect(self._handle_person_select_page_btn_clicked)
        self.show_scene_window_btn.clicked.connect(self._handle_show_scene_window_btn_clicked)
        self.callibration_page_btn.clicked.connect(self._handle_callibrate_page_btn_clicked)
        
        self.set_can_show_networking_page(self.vm.can_show_networking_page())
        self.set_can_show_offline_project_select_page(self.vm.can_show_offline_project_select_page())
        self.set_can_show_person_select_page(self.vm.can_show_person_select_page())
        self.camera_page_btn.click()
        
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.addButton(self.camera_page_btn)
        self.btn_group.addButton(self.networking_page_btn)
        self.btn_group.addButton(self.offine_project_select_page_btn)
        self.btn_group.addButton(self.person_select_page_btn)
        self.btn_group.addButton(self.tracking_page_btn)
        self.btn_group.addButton(self.callibration_page_btn)

        self.actions_group = QActionGroup(self)
        self.actions_group.setExclusive(True)
        self.actions_group.addAction(self.action_run_online)
        self.actions_group.addAction(self.action_run_offline)
        self.action_run_online.triggered.connect(self._handle_action_run_online_triggered)
        self.action_run_offline.triggered.connect(self._handle_action_run_offline_triggered)
        if self.vm.running_online():
            self.action_run_online.trigger()
        else:
            self.action_run_offline.trigger()

        
    @Slot(bool)
    def _handle_action_run_online_triggered(self, is_triggered:bool):
        if is_triggered:
            self.vm.set_run_online()

    @Slot(bool)
    def _handle_action_run_offline_triggered(self, is_triggered:bool):
        if is_triggered:
            self.vm.set_run_offline()

    @Slot(bool)
    def _observe_can_show_networking_page(self, can_show:bool):
        self.set_can_show_networking_page(can_show)

    def set_can_show_networking_page(self, can_show:bool):
        if can_show:
            self.networking_page_btn.setEnabled(True)
            self.networking_page_btn.setVisible(True)
            if self.stackedWidget.currentWidget() == self.page_network:
                self.navigate_camera_page() # TODO: navigate to empty page
        else:
            self.networking_page_btn.setEnabled(False)
            self.networking_page_btn.setVisible(False)
            

    @Slot(bool)
    def _observe_can_show_offline_project_select_page(self, can_show:bool):
        self.set_can_show_offline_project_select_page(can_show)

    def set_can_show_offline_project_select_page(self, can_show:bool):
        if can_show:
            self.offine_project_select_page_btn.setEnabled(True)
            self.offine_project_select_page_btn.setVisible(True)
            if self.stackedWidget.currentWidget() == self.page_offline_project_select:
                self.camera_page_btn.click() # TODO: navigate to empty page
        else:
            self.offine_project_select_page_btn.setEnabled(False)
            self.offine_project_select_page_btn.setVisible(False)
    
    @Slot(bool)
    def _observe_can_show_person_select_page_changed(self, can_show:bool):
        self.set_can_show_person_select_page(can_show)

    def set_can_show_person_select_page(self, can_show:bool):
        self.person_select_page_btn.setEnabled(can_show)
        if can_show and self.stackedWidget.currentWidget() == self.page_select_person:
            self.camera_page_btn.click()

    def navige_empty(self):
        self.stackedWidget.setCurrentIndex(-1)
        if btn:=self.btn_group.checkedButton():
            btn.setChecked(False)

    @Slot()
    def _handle_show_scene_window_btn_clicked(self):
        self.scene_window.bring_to_front()

    @Slot()
    def _handle_camera_page_btn_clicked(self):
        self.navigate_camera_page()

    @Slot()
    def _handle_networking_page_btn_clicked(self):
        self.navigate_networking_page()

    @Slot()
    def _handle_offline_project_select_page_btn_clicked(self):
        self.navigate_offline_project_select_page()

    @Slot()
    def _handle_callibrate_page_btn_clicked(self):
        self.stackedWidget.setCurrentWidget(self.page_callibration)

    @Slot()
    def _handle_tracking_page_btn_clicked(self):
        self.navigate_tracking_page()

    @Slot()
    def navigate_camera_page(self):
        # self.camera_page_btn.setChecked(True)
        self.stackedWidget.setCurrentWidget(self.page_camera)

    @Slot()
    def navigate_networking_page(self):
        # self.networking_page_btn.setChecked(True)
        self.stackedWidget.setCurrentWidget(self.page_network)

    @Slot()
    def navigate_offline_project_select_page(self):
        # self.offine_project_select_page_btn.setChecked(True)
        self.stackedWidget.setCurrentWidget(self.page_offline_project_select)

    @Slot()
    def _handle_person_select_page_btn_clicked(self):
        # self.person_select_page_btn.set
        self.stackedWidget.setCurrentWidget(self.page_select_person)

    
    @Slot()
    def navigate_tracking_page(self):
        # self.tracking_page_btn.setChecked(True)
        self.stackedWidget.setCurrentWidget(self.page_tracking)

    @Slot()
    def closeEvent(self, event: QCloseEvent) -> None:
        # print('close event')
        self.scene_window.close()
        self.vm.close()
        return super().closeEvent(event)

