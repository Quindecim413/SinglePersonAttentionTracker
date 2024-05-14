from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QFrame, QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton, QAbstractButton, QPushButton, QLabel, QFileDialog
from common.collections.observing_items import Item, ItemsCollection
from common.collections.projects import ActiveProjectDataCollection, SelectedProjectDataItem, AvailableProjectDataItem, ProjectsDataCollection
from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.project_data import AttentionProjectData
from common.services.scene.repo import AttentionProjectsRepo

from common.widgets.options import AvailableItemViewFactory, ItemView, ItemsCollectionView, SelectItemsContainer, SelectedItemViewFactory



class ProjectDataWidgetFactory(Protocol):
    def __call__(self, /, project_data:AttentionProjectData) -> QWidget:
        ...

class ExpandedProjectDataWidgetFactory(ProjectDataWidgetFactory):
    ...

class ShortProjectDataWidgetFactory(ProjectDataWidgetFactory):
    ...


class AvailableProjectDataOptionItem(ItemView):
    def __init__(self, 
                 project_data_item:AvailableProjectDataItem,
                 content:QWidget) -> None:
        super().__init__(project_data_item)
        self.project_data_item = project_data_item
        self.project_data_item.is_loaded_changed.connect(self._observe_is_loaded_changed)
        self.load_btn = QPushButton()
        self.load_btn.setCheckable(True)
        self.load_btn.clicked.connect(self._load_btn_clicked)
        self.load_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        hbox = QHBoxLayout()
        hbox.addWidget(content)
        hbox.addWidget(self.load_btn)
        
        w = QWidget()
        w.setLayout(hbox)
        self.set_content(w)
        self.set_loaded(self.project_data_item.is_loaded())

    @Slot()
    def _load_btn_clicked(self):
        self.project_data_item.load_project()

    @Slot(bool)
    def _observe_is_loaded_changed(self, is_loaded:bool):
        self.set_loaded(is_loaded)

    def set_loaded(self, is_loaded:bool):
        text = 'Загружено' if is_loaded else 'Загрузить'
        enabled = not is_loaded
        self.load_btn.setEnabled(enabled)
        self.load_btn.setText(text)
        self.load_btn.setChecked(is_loaded)


class SelectedProjectOptionItem(ItemView):
    def __init__(self, 
                 project_data_item:SelectedProjectDataItem,
                 content:QWidget,
                 ) -> None:
        super().__init__(project_data_item)
        self.project_data_item = project_data_item
        self.project_data_item
        self.unload_btn = QPushButton('Выгрузить')
        self.unload_btn.clicked.connect(self._unload_clicked)
        hbox = QHBoxLayout()
        hbox.addWidget(content)
        hbox.addWidget(self.unload_btn)
        w = QWidget()
        w.setLayout(hbox)
        self.set_content(w)

    def _unload_clicked(self):
        self.project_data_item.unload_project()


class SelectedProjectDataOptionItemFactory(SelectedItemViewFactory[SelectedProjectDataItem]):
    def __init__(self, project_data_widget_factory:ExpandedProjectDataWidgetFactory) -> None:
        super().__init__()
        self._project_data_widget_factory = project_data_widget_factory

    def __call__(self, item: SelectedProjectDataItem) -> ItemView[SelectedProjectDataItem]:
        return SelectedProjectOptionItem(item, self._project_data_widget_factory(item.project_data()))


class AvailableProjectDataOptionItemFactory(AvailableItemViewFactory[AvailableProjectDataItem]):
    def __init__(self, project_data_widget_factory:ShortProjectDataWidgetFactory) -> None:
        super().__init__()
        self._project_data_widget_factory = project_data_widget_factory

    def __call__(self, item: AvailableProjectDataItem) -> ItemView[AvailableProjectDataItem]:
        return AvailableProjectDataOptionItem(item, self._project_data_widget_factory(item.project_data()))


class ProjectDataSelectionWidget(QWidget):
    def __init__(self, 
                 projects_data_collection:ProjectsDataCollection,
                 active_project_data_collection:ActiveProjectDataCollection,
                 short_project_data_widget_factory:ShortProjectDataWidgetFactory,
                 expanded_project_data_widget_factory:ExpandedProjectDataWidgetFactory,
                 ) -> None:
        super().__init__()

        self.select_options_container = SelectItemsContainer(active_project_data_collection,
                                                               projects_data_collection,
                                                               SelectedProjectDataOptionItemFactory(expanded_project_data_widget_factory),
                                                               AvailableProjectDataOptionItemFactory(short_project_data_widget_factory))
        
        self.select_options_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Выбор используемого проекта'))
        
        vbox.addWidget(self.select_options_container)

        
        # frame = QFrame()
        # some_layout = QVBoxLayout()
        # frame.setLayout(some_layout)
        # some_layout.addWidget(self.select_options_container)
        # some_layout.addStretch(1)
        # frame.setLayout(some_layout)
        # frame.setFrameShadow(QFrame.Shadow.Sunken)
        # frame.setFrameShape(QFrame.Shape.Panel)
        # vbox.addWidget(frame)

        
        self.setLayout(vbox)