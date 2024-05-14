from PySide6.QtCore import QMimeData, Slot, Signal
from common.collections.observing_items import Item, ItemsCollection
from common.collections.scene_element import ObservingSceneElementItem
from common.domain.interfaces import AttentionScene, Person
from common.services.active_person import ActivePersonSelector
from common.services.scene.initializer import AttentionSceneInitializerService


class PersonInSceneItem(ObservingSceneElementItem):
    def __init__(self,
                 person:Person) -> None:
        super().__init__(person)
        self._person = person

    def person(self) -> Person:
        return self._person


class PersonsInSceneCollection(ItemsCollection[PersonInSceneItem]):
    def __init__(self, scene:AttentionScene|None=None) -> None:
        super().__init__()
        self._scene:AttentionScene|None = None
        self.set_scene(scene)

    def set_scene(self, scene:AttentionScene|None):
        if self._scene == scene:
            return
        self.clear()
        if self._scene:
            self._scene.disconnect(self)
        
        self._scene = scene
        if self._scene:
            self._scene.person_created.connect(self._observe_person_created)
            for person in self._scene.persons():
                self.add_item(PersonInSceneItem(person))

    @Slot(Person)
    def _observe_person_created(self, person:Person):
        self.add_item(PersonInSceneItem(person))

    def persons(self) -> list[Person]:
        return [item.person() for item in self.items()]

    def create_person(self):
        if self._scene:
            self._scene.create_person()


class AvailablePersonItem(ObservingSceneElementItem):
    is_active_changed = Signal(bool)
    def __init__(self, 
                 person:Person,
                 active_person_selector:ActivePersonSelector
                 ) -> None:
        super().__init__(person)
        self._person = person
        self._active_person_selector = active_person_selector
        self._old_is_active = self.is_selected()
        
        self._active_person_selector.active_person_changed.connect(self._observe_active_person_changed)

    @Slot()
    def _observe_active_person_changed(self):
        
        self.is_active_changed.emit(self.is_selected())

    def person(self):
        return self._person

    def make_active(self):
        self._active_person_selector.set_active_person(self._person)
    
    def is_selected(self):
        if active_person:=self._active_person_selector.active_person():
            return active_person.element_id() == self._person.element_id()
        return False
    
    
class SelectedPersonItem(ObservingSceneElementItem):
    def __init__(self,
                 person:Person,
                 active_person_selector:ActivePersonSelector) -> None:
        super().__init__(person)
        self._person = person
        self._active_person_selector = active_person_selector
        self._active_person_selector.active_person_changed.connect(self._observe_active_person_changed)

    def person(self):
        return self._person
    
    def make_not_active(self):
        self._active_person_selector.set_active_person(None)

    @Slot()
    def _observe_active_person_changed(self):
        active_person = self._active_person_selector.active_person()
        if active_person is None or active_person.element_id() != self._person.element_id():
            self.remove_item()


class AvailablePersonsCollection(ItemsCollection[AvailablePersonItem]):
    def __init__(self, 
                 active_person_selector:ActivePersonSelector,
                 scene_initializer:AttentionSceneInitializerService) -> None:
        super().__init__()
        self._scene:AttentionScene|None = None
        self._active_person_selector = active_person_selector
        self._scene_initializer = scene_initializer
        self._scene_initializer.attention_project_changed.connect(self._observe_project_changed)
        
        self._update_with_current_project()

    @Slot()
    def _observe_active_person_selector_changed(self):
        self._update_with_current_project()

    @Slot()
    def _observe_project_changed(self):
        self._update_with_current_project()
    
    def _update_with_current_project(self):
        project = self._scene_initializer.project()
        scene = project.scene() if project is not None else None
        if self._scene is not None:
            self._scene.disconnect(self)
        self._scene = scene
        self.clear()
        if self._scene:
            self._scene.person_created.connect(self._observe_person_created)
            for person in self._scene.persons():
                self.add_item(AvailablePersonItem(person, self._active_person_selector))

    @Slot(Person)
    def _observe_person_created(self, person:Person):
        self.add_item(AvailablePersonItem(person, self._active_person_selector))


class SelectedPersonCollection(ItemsCollection[SelectedPersonItem]):
    def __init__(self, 
                 active_person_selector:ActivePersonSelector,
                 parent=None) -> None:
        super().__init__(parent)
        self._active_person_selector = active_person_selector
        self._active_person_selector.active_person_changed.connect(self._observe_active_person_changed)
        if active_person:=self._active_person_selector.active_person():
            self.add_item(SelectedPersonItem(active_person, self._active_person_selector))

    @Slot()
    def _observe_active_person_changed(self):
        if active_person:=self._active_person_selector.active_person():
            self.add_item(SelectedPersonItem(active_person, self._active_person_selector))
