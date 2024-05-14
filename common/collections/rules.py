from PySide6.QtCore import QMimeData, Slot
from common.collections.observing_items import Item, ItemsCollection
from common.collections.scene_element import ObservingSceneElementItem
from common.domain.interfaces import AttentionRule, AttentionScene, Person


class RuleForPersonItem(Item):
    def __init__(self, 
                 rule: AttentionRule,
                 person:Person) -> None:
        super().__init__()
        self._person = person
        self._rule = rule
        self._person.removed_from_rule.connect(self._observe_person_removed_from_rule)
        self._rule.removed_from_scene.connect(self._removed_from_scene)
        self._person.removed_from_scene.connect(self._removed_from_scene)
    
    def person(self):
        return self._person
    
    def rule(self):
        return self._rule

    @Slot()
    def _removed_from_scene(self):
        self.remove_item()

    @Slot(AttentionRule)
    def _observe_person_removed_from_rule(self, rule:AttentionRule):
        if self._rule.element_id() == rule.element_id():
            self.remove_item()



class RuleInSceneItem(ObservingSceneElementItem):
    def __init__(self,
                 rule:AttentionRule) -> None:
        super().__init__(rule)
        self._rule = rule
        self._rule.removed_from_scene.connect(self._handle_removed_from_scene)

    @Slot()
    def _handle_removed_from_scene(self):
        self.remove_item()

    def rule(self) -> AttentionRule:
        return self._rule


class RulesForPersonCollection(ItemsCollection[RuleForPersonItem]):
    def __init__(self, person:Person|None) -> None:
        super().__init__()
        self._person = person
        self.set_person(person)

    def set_person(self, person:Person|None):
        if self._person:
            self._person.disconnect(self)
        
        self.clear()
        self._person = person
        if self._person:
            self._person.added_to_rule.connect(self._observe_person_added_to_rule)
            self._person.removed_from_scene.connect(self._observe_person_removed_from_scene)
            for rule in self._person.rules():
                self.add_item(RuleForPersonItem(rule, self._person))
    
    @Slot()
    def _observe_person_removed_from_scene(self):
        self.set_person(None)

    @Slot(object)
    def _observe_person_added_to_rule(self, rule:AttentionRule):
        if not isinstance(rule, AttentionRule):
            return
        if not self._person:
            return
        self.add_item(RuleForPersonItem(rule, self._person))


class RulesInSceneCollection(ItemsCollection[RuleInSceneItem]):
    def __init__(self, scene:AttentionScene) -> None:
        super().__init__()
        self._scene = scene
        self._scene.attention_rule_created.connect(self._observe_rule_created)
        for rule in self._scene.attention_rules():
            self.add_item(RuleInSceneItem(rule))

    # def handle_mimedata(self, mimedata: QMimeData):
    #     return super().handle_mimedata(mimedata)

    @Slot(AttentionRule)
    def _observe_rule_created(self, rule:AttentionRule):
        self.add_item(RuleInSceneItem(rule))

    def create_rule(self):
        self._scene.create_attention_rule()
