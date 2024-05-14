from typing import Callable
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from dependency_injector.wiring import inject, Provide
from common.domain.interfaces import SceneObj

from common.widgets.preview_expand import PreviewExpandWidget
from configurator_app.scene_objs_page.preview_item import SceneObjItemFactory
from configurator_app.scene_objs_page.vm import ConfigureSceneObjsPageVM
from dependency_injector.providers import Factory


class ConfigureSceneObjsPage(QWidget):

    def __init__(self,  
                 vm:ConfigureSceneObjsPageVM,
                 item_factory:SceneObjItemFactory,
                 parent=None,) -> None:
        super().__init__(parent)
        self.setMinimumSize(500, 500)

        self.vm = vm
        self.preview_configure_widget = PreviewExpandWidget(vm.scene_objs_collection(),
                                                            item_factory)
        
        self.setup_ui()
    
    def setup_ui(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_configure_widget)
        self.setLayout(vbox)
