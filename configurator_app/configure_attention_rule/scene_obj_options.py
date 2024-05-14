from abc import abstractmethod
from pathlib import Path
from typing import Any, Callable, Protocol, TypeAlias
from common.collections.scene_obj_in_rule import ObserveSceneObjOptionsCollection, SceneObjItem
from common.domain.interfaces import SceneObj
from common.widgets.options import ItemView, ItemViewFactory, ItemsCollectionView
from common.widgets.preview_scene_obj import SceneObjPreviewWidget
from .in_and_not_options import InRuleAndNotItemsContainer
from .vm import  SceneObjsInRuleCollection, SceneObjsNotInRuleCollection
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Slot
from PySide6.QtGui import QPixmap
from dependency_injector.wiring import inject, Provide


SceneObjPreviewWFactory:TypeAlias = Callable[[SceneObj], QWidget]

class SceneObjOption(ItemView):
    def __init__(self, 
                 item:SceneObjItem,
                 ) -> None:
        super().__init__(item, draggable=True)
        self.set_content(SceneObjPreviewWidget(item.scene_obj()))

class SceneObjInRuleOption(SceneObjOption):
    def make_mime_pixmap(self):
        return QPixmap(Path(__file__).parent.parent/'src/remove-obj.png')


class SceneObjNotInRuleOption(SceneObjOption):
    def make_mime_pixmap(self):
        return QPixmap(Path(__file__).parent.parent/'src/add-obj.png')


class SceneObjOptionFactory(ItemViewFactory[SceneObjItem]):
    @abstractmethod
    def __call__(self, item: SceneObjItem) -> ItemView:
        ...


class SceneObjInRuleOptionFactory(SceneObjOptionFactory):
    def __call__(self, item: SceneObjItem) -> ItemView:
        return SceneObjInRuleOption(item)
    
class SceneObjNotInRuleOptionFactory(SceneObjOptionFactory):
    def __call__(self, item: SceneObjItem) -> ItemView:
        return SceneObjNotInRuleOption(item)

class SceneObjsForRuleSelectWidget(QWidget):
    def __init__(self, 
                 scene_objs_in_rule:SceneObjsInRuleCollection,
                 scene_objs_not_in_rule:SceneObjsNotInRuleCollection,
                 ) -> None:
        super().__init__()
        self.in_options_view = ItemsCollectionView(scene_objs_in_rule, SceneObjInRuleOptionFactory())
        self.not_in_options_view = ItemsCollectionView(scene_objs_not_in_rule, SceneObjNotInRuleOptionFactory())
        self.options_view = InRuleAndNotItemsContainer(self.in_options_view, self.not_in_options_view)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Перетащите объекты сцены в соответствующие колонки'))
        vbox.addWidget(self.options_view)
        self.setLayout(vbox)