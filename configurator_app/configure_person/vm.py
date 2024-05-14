from PySide6.QtCore import Signal, QObject, Slot
from PySide6.QtGui import QColor, QVector3D, QQuaternion
from common.domain.interfaces import Person


class PersonConfigureVM(QObject):
    stop_editing = Signal()
    view_name_changed = Signal(str)
    show_selected_changed = Signal(bool)
    camera_position_changed = Signal(QVector3D) # 3 x float
    camera_rotation_changed = Signal(QQuaternion) # 3 x float
    head_color_chaged = Signal(QColor)

    def __init__(self, person:Person) -> None:
        super().__init__()
        self.person = person
        self.person.removed_from_scene.connect(self._observe_removed_from_scene)
        self.person.element_name_changed.connect(self._observe_element_name_changed)
        self.person.camera_position_changed.connect(self._observe_camera_position_changed)
        self.person.camera_rotation_changed.connect(self._observe_camera_rotation_changed)
        self.person.head_color_changed.connect(self._observe_head_color_changed)
        self.person.is_selected_changed.connect(self._observe_is_selected_changed)

    @Slot(bool)
    def _observe_is_selected_changed(self, is_selected:bool):
        self.show_selected_changed.emit(is_selected)

    @Slot()
    def _observe_removed_from_scene(self,):
        self.stop_editing.emit()

    @Slot(str)
    def _observe_element_name_changed(self, name):
        self.view_name_changed.emit(name)

    @Slot(tuple)
    def _observe_camera_position_changed(self, cam_pos):
        self.camera_position_changed.emit(cam_pos)

    @Slot(tuple)
    def _observe_camera_rotation_changed(self, cam_rot):
        self.camera_rotation_changed.emit(cam_rot)

    @Slot(QColor)
    def _observe_head_color_changed(self, color:QColor):
        self.head_color_chaged.emit(color)

    def view_id(self):
        return str(self.person.element_id())
    
    def name(self):
        return self.person.element_name()
    
    def set_name(self, name:str):
        self.person.set_element_name(name)

    def head_color(self):
        return self.person.head_color()
    
    def set_head_color(self, color:QColor):
        self.person.set_head_color(color)

    def camera_position(self):
        return self.person.camera_position()

    def set_camera_position(self, pos:QVector3D):
        self.person.set_camera_position(pos)

    def camera_rotation(self):
        return self.person.camera_rotation()

    def set_camera_rotation(self, rot:QQuaternion):
        self.person.set_camera_rotation(rot)

    def show_selected(self):
        return self.person.is_selected()
    
    def toggle_show_selected(self):
        self.person.set_selected(not self.person.is_selected())

    def remove_element(self):
        self.person.remove_from_scene()
