
from PySide6.QtCore import Qt, Slot, Signal, QSize, QObject
from common.collections.persons import PersonsInSceneCollection
from common.domain.interfaces import AttentionScene, Person


class ConfigurePersonsPageVM(QObject):
    def __init__(self,
                 scene:AttentionScene
                 ) -> None:
        super().__init__()
        self._persons_in_scene = PersonsInSceneCollection(scene)

    def persons_collection(self):
        return self._persons_in_scene
    
    def create_person(self):
        self._persons_in_scene.create_person()
