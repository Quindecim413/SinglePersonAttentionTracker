from abc import abstractmethod
from datetime import timedelta
import json
from PySide6.QtCore import QObject, Slot, Signal, QMimeData
from common.collections.observing_items import ItemsCollection, Item
from common.domain.interfaces import AttentionRule, AttentionScene, Person, SceneElement, SceneObj


def create_scene_obj_mimedata(scene_obj:SceneObj):
    mime = QMimeData() 
    mime.setText(json.dumps({'scene_obj_id': scene_obj.element_id()}, ensure_ascii=False))
    return mime

def restore_scene_obj_from_mimedata(mimedata:QMimeData, scene:AttentionScene):
    if not mimedata.hasText():
            return
    try:
        scene_obj_id = json.loads(mimedata.text())['scene_obj_id']
        scene_obj = scene.scene_objs_by_id()[scene_obj_id]
    except Exception as e:
        print('Error restore_scene_obj_from_mimedata:', 'mime text:', mimedata.text(), ', err:', str(e))
        return
    
    return scene_obj


class SceneObjItem(Item):
    def __init__(self, scene_obj:SceneObj,
                 rule:AttentionRule) -> None:
        super().__init__()
        self._rule = rule
        self._scene_obj = scene_obj

    def scene_obj(self):
        return self._scene_obj
    
    def rule(self):
        return self._rule

    def make_mimedata(self):
        return create_scene_obj_mimedata(self._scene_obj)


class SceneObjInRuleItem(SceneObjItem):
    def __init__(self, scene_obj:SceneObj,
                 rule:AttentionRule) -> None:
        super().__init__(scene_obj, rule)
        self.rule().scene_obj_removed.connect(self._observe_scene_obj_removed_from_rule)
    
    @Slot(SceneObj)
    def _observe_scene_obj_removed_from_rule(self, scene_obj:SceneObj):
        if self.scene_obj().element_id() == scene_obj.element_id():
            self.remove_item()


class SceneObjNotInRuleItem(SceneObjItem):
    def __init__(self, scene_obj:SceneObj,
                 rule:AttentionRule) -> None:
        super().__init__(scene_obj, rule)
        self.rule().scene_obj_added.connect(self._observe_scene_obj_added_to_rule)
    
    @Slot(SceneObj)
    def _observe_scene_obj_added_to_rule(self, scene_obj:SceneObj):
        if self.scene_obj().element_id() == scene_obj.element_id():
            self.remove_item()


class ObserveSceneObjOptionsCollection(ItemsCollection[SceneObjItem]):
    scene_obj_added = Signal(SceneObjItem)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.item_added.connect(self._observe_item_added)
    
    def scene_obj_options(self):
        return self.items()
    
    @Slot(Item)
    def _observe_item_added(self, item:Item):
        self.scene_obj_added.emit(item)


class SceneObjsInRuleCollection(ObserveSceneObjOptionsCollection):
    def __init__(self, rule:AttentionRule) -> None:
        super().__init__()
        self.rule = rule
        self.rule.scene_obj_added.connect(self._observe_scene_obj_added_to_rule)
        for scene_obj in self.rule.scene_objs():
            self.add_item(SceneObjInRuleItem(scene_obj, self.rule))
    
    @Slot(SceneObj)
    def _observe_scene_obj_added_to_rule(self, scene_obj:SceneObj):
        s_vm = SceneObjInRuleItem(scene_obj, self.rule)
        self.add_item(s_vm)

    def handle_mimedata(self, mimedata:QMimeData):
        scene_obj = restore_scene_obj_from_mimedata(mimedata, self.rule.scene())
        if scene_obj is None:
            return
        if scene_obj not in self.rule:
            self.rule.add_scene_obj(scene_obj)


class SceneObjsNotInRuleCollection(ObserveSceneObjOptionsCollection):
    def __init__(self, rule:AttentionRule) -> None:
        super().__init__()
        self.rule = rule
        self.rule.scene_obj_removed.connect(self._observe_scene_obj_removed_from_rule)
        
        for scene_obj in self.rule.scene().scene_objs():
            if scene_obj not in self.rule:
                self.add_item(SceneObjNotInRuleItem(scene_obj, self.rule))
    
    @Slot(SceneObj)
    def _observe_scene_obj_removed_from_rule(self, scene_obj:SceneObj):
        s_vm = SceneObjNotInRuleItem(scene_obj, self.rule)
        self.add_item(s_vm)
    
    def handle_mimedata(self, mimedata:QMimeData):
        scene_obj = restore_scene_obj_from_mimedata(mimedata, self.rule.scene())
        if scene_obj is None:
            return
        if scene_obj in self.rule:
            self.rule.remove_scene_obj(scene_obj)