from PySide6.QtCore import QObject, Signal, Slot

from common.collections.observing_items import Item, ItemsCollection
from common.collections.persons import  PersonInSceneItem, PersonsInSceneCollection

from common.services.scene.initializer import AttentionSceneInitializerService
from common.services.scene.project import AttentionProject
from web.domain.exposed_person import ExposedPerson


class ExposedPersonItem(Item):
    def __init__(self, 
                 exposed_person:ExposedPerson,
                 ) -> None:
        super().__init__()
        self._exposed_person = exposed_person
        self._exposed_person._person.removed_from_scene.connect(self._person_removed)

    @Slot()
    def _person_removed(self):
        self.remove_item()

    def exposed_person(self) -> ExposedPerson:
        return self._exposed_person


class ExposedPersonsCollection(ItemsCollection[ExposedPersonItem]):
    def __init__(self, scene_initializer:AttentionSceneInitializerService) -> None:
        super().__init__()
        self._scene_initializer = scene_initializer
        self._scene_initializer.attention_project_changed.connect(self._project_changed)
        self._project:AttentionProject|None = None
        self._persons_in_scene_collection = PersonsInSceneCollection()
        self._persons_in_scene_collection.item_added.connect(self._person_in_scene_added)

    @Slot(PersonInSceneItem)
    def _person_in_scene_added(self, person_in_scene_item:PersonInSceneItem):
        item = ExposedPersonItem(ExposedPerson(person_in_scene_item.person()))
        self._scene_initializer.attention_project_changed.connect(item.remove_item)
        self.add_item(item)

    def exposed_persons(self) -> list[ExposedPerson]:
        return [item.exposed_person() for item in self.items()]

    @Slot()
    def _project_changed(self):
        self._set_project(self._scene_initializer.project())

    def _set_project(self, project:AttentionProject|None):
        if self._project == project:
            return
        
        self.clear()
        self._project = project

        if project is None:
            self._persons_in_scene_collection.set_scene(None)
        else:
            self._persons_in_scene_collection.set_scene(project.scene())

