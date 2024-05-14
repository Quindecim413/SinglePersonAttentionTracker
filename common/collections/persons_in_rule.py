import json
from PySide6.QtCore import QObject, Slot, Signal, QMimeData
from common.collections.observing_items import ItemsCollection, Item
from common.domain.interfaces import AttentionRule, AttentionScene, Person


def create_person_mimedata(person:Person):
    mime = QMimeData() 
    mime.setText(json.dumps({'person_id': person.element_id()}, ensure_ascii=False))
    return mime


def restore_person_from_mimedata(mimedata:QMimeData, scene:AttentionScene):
    if not mimedata.hasText():
            return
    try:
        person_id = json.loads(mimedata.text())['person_id']
        person = scene.persons_by_id()[person_id]
    except Exception as e:
        print('Error restore_person_from_mimedata:', str(e))
        return
    
    return person


class PersonItem(Item):
    def __init__(self, 
                 person:Person,
                 rule:AttentionRule) -> None:
        super().__init__()
        self._rule = rule
        self._person = person
    
    def person(self):
        return self._person
    
    def rule(self):
        return self._rule
    
    def make_mimedata(self):
        return create_person_mimedata(self._person)


class PersonInRuleItem(PersonItem):
    def __init__(self, person:Person,
                 rule:AttentionRule) -> None:
        super().__init__(person, rule)
        self.rule().person_removed.connect(self._observe_person_removed_from_rule)
    
    @Slot(Person)
    def _observe_person_removed_from_rule(self, person:Person):
        if self.person().element_id() == person.element_id():
            self.remove_item()
    

class PersonNotInRuleItem(PersonItem):
    def __init__(self, person:Person,
                 rule:AttentionRule) -> None:
        super().__init__(person, rule)
        self.rule().person_added.connect(self._observe_person_added_to_rule)
    
    @Slot(Person)
    def _observe_person_added_to_rule(self, person:Person):
        if self.person().element_id() == person.element_id():
            self.remove_item()

class BasePersonsCollection(ItemsCollection[PersonItem]):
    person_added = Signal(PersonItem)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.item_added.connect(self._observe_item_added)

    @Slot(Item)
    def _observe_item_added(self, item):
        self.person_added.emit(item)

    def person_options(self):
        return self.items()


class PersonsInRuleCollection(BasePersonsCollection):
    def __init__(self, rule:AttentionRule) -> None:
        super().__init__()
        self.rule = rule
        self.rule.person_added.connect(self._observe_person_added_to_rule)

        for person in self.rule.persons():
            self.add_item(PersonInRuleItem(person, self.rule))
        
    @Slot(Person)
    def _observe_person_added_to_rule(self, person:Person):
        p_vm = PersonInRuleItem(person, self.rule)
        self.add_item(p_vm)
    
    def handle_mimedata(self, mimedata:QMimeData):
        person = restore_person_from_mimedata(mimedata, self.rule.scene())
        if person is None:
            return
        if person not in self.rule:
            self.rule.add_person(person)


class PersonsNotInRuleCollection(BasePersonsCollection):
    def __init__(self, rule:AttentionRule) -> None:
        super().__init__()
        self.rule = rule
        self.rule.person_removed.connect(self._observe_person_removed_from_rule)
        self.rule.scene().person_created.connect(self._observe_new_person_created)
        
        for person in self.rule.scene().persons():
            if person not in self.rule:
                self.add_item(PersonNotInRuleItem(person, self.rule))

    @Slot(Person)
    def _observe_person_removed_from_rule(self, person:Person):
        p_vm = PersonNotInRuleItem(person, self.rule)
        self.add_item(p_vm)

    @Slot(Person)
    def _observe_new_person_created(self, person:Person):
        p_vm = PersonNotInRuleItem(person, self.rule)
        self.add_item(p_vm)
    
    def handle_mimedata(self, mimedata:QMimeData):
        person = restore_person_from_mimedata(mimedata, self.rule.scene())
        if person is None:
            return
        if person in self.rule:
            self.rule.remove_person(person)