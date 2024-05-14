from typing import Protocol
from PySide6.QtWidgets import QWidget
from common.collections.projects import AvailableProjectDataItem
from common.services.scene.project_data import AttentionProjectData
from dependency_injector.wiring import inject, Provide
from common.widgets.preview_expand import ItemViewFactory


class PreviewProjectDataWidgetFactory(Protocol):
    def __call__(self, project_data:AttentionProjectData) -> QWidget:
        ...

class ConfigureProjectDataWidgetFactory(Protocol):
    def __call__(self, project_data:AttentionProjectData) -> QWidget:
        ...


class ProjectDataItemFactory(ItemViewFactory[AvailableProjectDataItem]):
    def __init__(self,
                 preview_widget_factory:PreviewProjectDataWidgetFactory,
                 configure_widget_factory:ConfigureProjectDataWidgetFactory,) -> None:
        super().__init__()
        self.preview_widget_factory = preview_widget_factory
        self.configure_widget_factory = configure_widget_factory

    def create_preview_widget(self, item: AvailableProjectDataItem) -> QWidget:
        return self.preview_widget_factory(item.project_data())
    
    def create_expanded_widget(self, item: AvailableProjectDataItem) -> QWidget:
        return self.configure_widget_factory(item.project_data())