from PySide6.QtCore import QObject
from common.collections.scene_objs import SceneObjsInSceneCollection
from common.domain.interfaces import AttentionScene


class ConfigureSceneObjsPageVM(QObject):
    def __init__(self, 
                 scene:AttentionScene
                 ) -> None:
        super().__init__()
        self._scene_objs_collection = SceneObjsInSceneCollection(scene)

    def scene_objs_collection(self):
        return self._scene_objs_collection