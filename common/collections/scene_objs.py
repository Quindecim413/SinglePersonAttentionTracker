from PySide6.QtCore import QMimeData, Slot
from common.collections.observing_items import Item, ItemsCollection
from common.collections.scene_element import ObservingSceneElementItem
from common.domain.interfaces import AttentionRule, AttentionScene, Person, SceneObj


def _have_shared_rules(person:Person, scene_obj:SceneObj) -> bool:
    person_rules = set(map(lambda r:r.element_id(), person.rules()))
    scene_obj_rules = set(map(lambda r:r.element_id(), scene_obj.rules()))
    return len(person_rules.intersection(scene_obj_rules)) > 0
        

class SceneObjForPersonItem(Item):
    def __init__(self, 
                 scene_obj:SceneObj,
                 person:Person) -> None:
        super().__init__()
        self._scene_obj = scene_obj
        self._person = person
        self._scene_obj.removed_from_rule.connect(self._removed_from_rule)
        self._person.removed_from_rule.connect(self._removed_from_rule)
        if not _have_shared_rules(self._person, self._scene_obj):
            self.remove_item()

    def scene_obj(self):
        return self._scene_obj
    
    def person(self):
        return self._person

    @Slot(AttentionRule)
    def _removed_from_rule(self, rule:AttentionRule):
        if not _have_shared_rules(self._person, self._scene_obj):
            self.remove_item()



class SceneObjInSceneItem(ObservingSceneElementItem):
    def __init__(self,
                 scene_obj:SceneObj) -> None:
        super().__init__(scene_obj)
        self._scene_obj = scene_obj

    def scene_obj(self) -> SceneObj:
        return self._scene_obj


class SceneObjsInSceneCollection(ItemsCollection[SceneObjInSceneItem]):
    def __init__(self, scene:AttentionScene|None = None) -> None:
        super().__init__()
        if scene:
            self.set_scene(scene)
    
    def set_scene(self, scene:AttentionScene):
        self.clear()
        self._scene = scene
        for scene_obj in self._scene.scene_objs():
            self.add_item(SceneObjInSceneItem(scene_obj))

    # def handle_mimedata(self, mimedata: QMimeData):
    #     return super().handle_mimedata(mimedata)
