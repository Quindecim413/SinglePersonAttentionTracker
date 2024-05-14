from common.collections.observing_items import Item
from common.domain.interfaces import SceneElement
from PySide6.QtCore import Slot


class ObservingSceneElementItem(Item):
    def __init__(self, element:SceneElement) -> None:
        super().__init__()
        if not isinstance(element, SceneElement):
            raise TypeError()
        self._element = element
        self._element.removed_from_scene.connect(self._observe_element_removed)

    @Slot()
    def _observe_element_removed(self):
        self.remove_item()