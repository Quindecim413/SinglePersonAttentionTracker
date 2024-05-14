from PySide6.QtWidgets import QWidget
from common.collections.persons import PersonInSceneItem
from common.domain.interfaces import Person
from common.widgets.preview_expand import ItemViewFactory, PreviewItem
from typing import Protocol


class PreviewPersonWidgetFactory(Protocol):
    def __call__(self, person:Person) -> QWidget:
        ...

class ConfigurePersonWidgetFactory(Protocol):
    def __call__(self, person:Person) -> QWidget:
        ...
    

class PersonItemFactory(ItemViewFactory[PersonInSceneItem]):
    def __init__(self,
                 preview_widget_factory:PreviewPersonWidgetFactory,
                 configure_widget_factory:ConfigurePersonWidgetFactory,) -> None:
        super().__init__()
        self.preview_widget_factory = preview_widget_factory
        self.configure_widget_factory = configure_widget_factory

    def create_preview_widget(self, item: PersonInSceneItem) -> QWidget:
        return self.preview_widget_factory(item.person())
    
    def create_expanded_widget(self, item: PersonInSceneItem) -> QWidget:
        return self.configure_widget_factory(item.person())
