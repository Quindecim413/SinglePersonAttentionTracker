from typing import Protocol
from common.collections.scene_objs import SceneObjInSceneItem
from common.domain.interfaces import SceneObj
from PySide6.QtWidgets import QWidget
from common.widgets.preview_expand import ItemViewFactory, PreviewItem


class PreviewSceneObjWidgetFactory(Protocol):
    def __call__(self, scene_obj:SceneObj) -> QWidget:
        ...

class ConfigureSceneObjWidgetFactory(Protocol):
    def __call__(self, scene_obj:SceneObj) -> QWidget:
        ...


class SceneObjItemFactory(ItemViewFactory[SceneObjInSceneItem]):
    def __init__(self,
                 preview_widget_factory:PreviewSceneObjWidgetFactory,
                 configure_widget_factory:ConfigureSceneObjWidgetFactory,) -> None:
        super().__init__()
        self.preview_widget_factory = preview_widget_factory
        self.configure_widget_factory = configure_widget_factory

    def create_preview_widget(self, item: SceneObjInSceneItem) -> QWidget:
        return self.preview_widget_factory(item.scene_obj())
    
    def create_expanded_widget(self, item: SceneObjInSceneItem) -> QWidget:
        return self.configure_widget_factory(item.scene_obj())
