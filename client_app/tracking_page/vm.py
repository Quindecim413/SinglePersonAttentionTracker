from PySide6.QtCore import Qt, QTimer, Slot, QObject, Signal
from common.collections.observing_items import Item, ItemsCollection
from common.collections.persons import SelectedPersonCollection
from common.collections.rules import RuleForPersonItem
from common.collections.scene_objs import SceneObjForPersonItem
from common.domain.interfaces import AttentionRule, Person
from common.services.active_work_state import ActiveWorkState


class SceneObjsForSelectedPersonCollection(ItemsCollection[SceneObjForPersonItem]):
    def __init__(self, active_work_state:ActiveWorkState) -> None:
        super().__init__()
        self._workstate = active_work_state
        self._active_person:Person|None = None
        self._workstate.active_scene_changed.connect(self._observe_scene_changed)
        self._workstate.active_person_changed.connect(self._observe_active_person_changed)
        self._configure_scene_objs_in_scene()
        self._set_scene_with_person()

    @Slot()
    def _observe_scene_changed(self):
        self._configure_scene_objs_in_scene()
    
    def _configure_scene_objs_in_scene(self):
        self.clear()
        scene = self._workstate.active_scene()
        if not scene:
            return
        
        for scene_obj in scene.scene_objs():
            scene_obj.added_to_rule.connect(self._added_to_rule)
    
    @Slot()
    def _observe_active_person_changed(self):
        self._set_scene_with_person()

    def _set_scene_with_person(self):
        self.clear()
        person = self._workstate.active_person()
        scene = self._workstate.active_scene()
        if not (person and scene):
            return
        if self._active_person:
            self._active_person.disconnect(self)
        
        self._active_person = person
        self._active_person.added_to_rule.connect(self._added_to_rule)

        for scene_obj in scene.scene_objs():
            # Не наблюдаемые данным пользователем объекты сцены создадут элементы, которые будут сразу удалены
            self.add_item(SceneObjForPersonItem(scene_obj, person))

    @Slot(AttentionRule)
    def _added_to_rule(self, rule:AttentionRule):
        self._set_scene_with_person()
        # person = self._active_person
        # if not person:
        #     return
        # current_scene_objs_ids = set([item.scene_obj().element_id() for item in self.items()])
        # for scene_obj_in_rule in rule.scene_objs():
        #     if scene_obj_in_rule.element_id() not in current_scene_objs_ids:
        #         self.add_item(SceneObjForPersonItem(scene_obj_in_rule, person))


class RulesForSelectedPersonCollection(ItemsCollection[RuleForPersonItem]):
    def __init__(self, active_work_state:ActiveWorkState) -> None:
        super().__init__()
        self._workstate = active_work_state
        self._active_person:Person|None = None
        self._workstate.active_scene_changed.connect(self._observe_scene_changed)
        self._workstate.active_person_changed.connect(self._observe_active_person_changed)
        self._set_scene_with_person()

    @Slot()
    def _observe_scene_changed(self):
        self._set_scene_with_person()

    @Slot()
    def _observe_active_person_changed(self):
        self._set_scene_with_person()

    def _set_scene_with_person(self):
        self.clear()
        person = self._workstate.active_person()
        scene = self._workstate.active_scene()
        if not (person and scene):
            return
        if self._active_person:
            self._active_person.disconnect(self)
        
        self._active_person = person
        self._active_person.added_to_rule.connect(self._added_to_rule)

        for rule in scene.attention_rules():
            # Не наблюдаемые данным пользователем объекты сцены создадут элементы, которые будут сразу удалены
            self.add_item(RuleForPersonItem(rule, person))

    @Slot(AttentionRule)
    def _added_to_rule(self, rule:AttentionRule):
        self._set_scene_with_person()



class TrackingPageVM(QObject):
    show_no_person_selected_changed = Signal(bool)
    def __init__(self, 
                 selected_person_collection:SelectedPersonCollection,
                 scene_objs_for_selected_person_collection:SceneObjsForSelectedPersonCollection,
                 rules_for_selected_person_collection:RulesForSelectedPersonCollection,) -> None:
        super().__init__()
        self._selected_person_collection = selected_person_collection
        self._rules_for_active_person = rules_for_selected_person_collection
        self._scene_objs_for_selected_person_collection = scene_objs_for_selected_person_collection
        self._selected_person_collection.items_changed.connect(self._observe_selected_person_collection_changed)
        self._old_show_no_person_selected = self.show_no_person_selected()

    def show_no_person_selected(self) -> bool:
        return len(self._selected_person_collection) == 0

    @Slot()
    def _observe_selected_person_collection_changed(self):
        val = self.show_no_person_selected()
        if val != self._old_show_no_person_selected:
            self.show_no_person_selected_changed.emit(val)

    def selected_person_collection(self) -> SelectedPersonCollection:
        return self._selected_person_collection

    def rules_for_active_person_collection(self) -> RulesForSelectedPersonCollection:
        return self._rules_for_active_person

    def scene_objs_for_active_person_collection(self) -> SceneObjsForSelectedPersonCollection:
        return self._scene_objs_for_selected_person_collection
