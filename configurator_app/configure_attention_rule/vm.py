from abc import abstractmethod
from datetime import timedelta
import json
from PySide6.QtCore import QObject, Slot, Signal, QMimeData
from common.collections.observing_items import ItemsCollection, Item
from common.collections.persons_in_rule import PersonsInRuleCollection, PersonsNotInRuleCollection
from common.collections.scene_obj_in_rule import SceneObjsInRuleCollection, SceneObjsNotInRuleCollection
from common.domain.interfaces import AttentionRule, AttentionScene, Person, SceneElement, SceneObj


class AttentionRuleConfigureWidgetVM(QObject):
    stop_editing = Signal()
    visible_name_changed = Signal(str)
    seconds_without_attantion_changed = Signal(float)
    show_selected_changed = Signal(bool)

    def __init__(self, rule:AttentionRule) -> None:
        super().__init__()
        self.rule = rule
        self.rule.removed_from_scene.connect(self._observe_removed_from_scene)
        self.rule.element_name_changed.connect(self._observe_name_changed)
        self.rule.is_selected_changed.connect(self._observe_selected_changed)
        self.rule.without_attention_timedelta_changed.connect(self._observe_without_attention_timedelta_changed)
        self._scene_objs_in_rule_collection = SceneObjsInRuleCollection(self.rule)
        self._scene_objs_not_in_rule_collection = SceneObjsNotInRuleCollection(self.rule)
        self._persons_in_rule_collection = PersonsInRuleCollection(self.rule)
        self._persons_not_in_rule_collection = PersonsNotInRuleCollection(self.rule)

    @Slot()
    def _observe_removed_from_scene(self,):
        self.stop_editing.emit()

    @Slot(str)
    def _observe_name_changed(self, name:str):
        self.visible_name_changed.emit(name)

    @Slot(bool)
    def _observe_selected_changed(self, is_selected:bool):
        self.show_selected_changed.emit(is_selected)

    @Slot(timedelta)
    def _observe_without_attention_timedelta_changed(self, tdelta:timedelta):
        self.seconds_without_attantion_changed.emit(tdelta.total_seconds())
    
    def scene_objs_in_rule_collection(self):
        return self._scene_objs_in_rule_collection
    
    def scene_objs_not_in_rule_collection(self):
        return self._scene_objs_not_in_rule_collection
    
    def persons_in_rule_collection(self):
        return self._persons_in_rule_collection
    
    def persons_not_in_rule_collection(self):
        return self._persons_not_in_rule_collection
    
    def visible_id(self):
        return str(self.rule.element_id())

    def visible_name(self):
        return self.rule.element_name()
    
    def set_visible_name(self, name:str):
        self.rule.set_element_name(name)

    def show_selected(self):
        return self.rule.is_selected()
    
    def toggle_show_selected(self):
        self.rule.set_selected(not self.rule.is_selected())

    def remove_element(self):
        self.rule.remove_from_scene()

    def seconds_without_attention(self):
        return self.rule.without_attention_timedelta().total_seconds()
    
    def set_seconds_without_attention(self, sec:float):
        self.rule.set_without_attention_timedelta(timedelta(seconds=sec))

    # def add_person_with_mime_data(self, mimedata:QMimeData):
    #     person = restore_person_from_mimedata(mimedata, self.rule.scene())
    #     if person and person not in self.rule:
    #         self.rule.add_person(person)

    # def remove_user_with_mime_data(self, mimedata:QMimeData):
    #     person = restore_person_from_mimedata(mimedata, self.rule.scene())
    #     if person and person in self.rule:
    #         self.rule.remove_person(person)

    # def add_scene_obj_with_mime_data(self, mimedata:QMimeData):
    #     scene_obj = restore_scene_obj_from_mimedata(mimedata, self.rule.scene())
    #     if scene_obj and scene_obj not in self.rule:
    #         self.rule.add_scene_obj(scene_obj)
        
    # def remove_scene_obj_with_mimedata(self, mimedata:QMimeData):
    #     scene_obj = restore_scene_obj_from_mimedata(mimedata, self.rule.scene())
    #     if scene_obj and scene_obj in self.rule:
    #         self.rule.remove_scene_obj(scene_obj)
