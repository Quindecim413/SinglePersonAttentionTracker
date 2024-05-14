from datetime import timedelta
from PySide6.QtCore import Qt, Slot, Signal, QSize, QObject

from common.domain.interfaces import SceneObj


class SceneObjConfigureVM(QObject):
    stopped_editing = Signal()
    name_changed = Signal(str)
    keep_attention_seconds_changed = Signal(float)
    show_selected_changed = Signal(bool)

    def __init__(self, scene_obj:SceneObj) -> None:
        super().__init__()
        self.scene_obj = scene_obj
        self.scene_obj.removed_from_scene.connect(self._observe_removed)
        self.scene_obj.element_name_changed.connect(self._observe_element_name_changed)
        self.scene_obj.is_selected_changed.connect(self._observe_is_selected_changed)
        self.scene_obj.keep_attention_timedelta_changed.connect(self._handle_keep_attention_timedelta_changed)

    @Slot()
    def _observe_removed(self):
        self.stopped_editing.emit()

    @Slot(str)
    def _observe_element_name_changed(self, name):
        self.name_changed.emit(name)

    @Slot(bool)
    def _observe_is_selected_changed(self, is_selected):
        self.show_selected_changed.emit(is_selected)

    def keep_attention_seconds(self):
        return self.scene_obj.keep_attention_timedelta().total_seconds()

    def set_keep_attention_seconds(self, seconds:float):
        self.scene_obj.set_keep_attention_timedelta(timedelta(seconds=seconds))

    def view_id(self):
        return str(self.scene_obj.element_id())
    
    def name(self):
        return self.scene_obj.element_name()
    
    def set_name(self, name:str):
        self.scene_obj.set_element_name(name)

    def show_selected(self):
        return self.scene_obj.is_selected()
    
    def toggle_show_selected(self):
        self.scene_obj.set_selected(not self.scene_obj.is_selected())

    @Slot(timedelta)
    def _handle_keep_attention_timedelta_changed(self, tdelta:timedelta):
        self.keep_attention_seconds_changed.emit(tdelta.total_seconds())