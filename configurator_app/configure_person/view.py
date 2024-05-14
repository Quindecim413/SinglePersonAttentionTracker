from datetime import timedelta
from typing import cast
from PySide6.QtCore import Qt, Slot, Signal, QSize, QObject
from PySide6.QtWidgets import QMainWindow, QWidget, QToolBar, QLabel, QFrame, QSizePolicy,\
    QSplitter, QScrollArea, QVBoxLayout, QPushButton, QLineEdit, QDoubleSpinBox, QSpinBox, QGridLayout, QHBoxLayout
from PySide6.QtGui import QColor, QVector3D, QQuaternion
from colorpicker.colorpicker import ColorPicker
from .vm import PersonConfigureVM


class ConfigurePersonWidget(QWidget):
    def __init__(self, vm:PersonConfigureVM, parent=None) -> None:
        super().__init__(parent)
        self.vm = vm
        self.setup_ui()

        self.vm.stop_editing.connect(self.observe_stop_editing)
        self.vm.view_name_changed.connect(self.observe_person_name_changed)
        self.vm.head_color_chaged.connect(self.observe_head_color_changed)
        self.vm.camera_position_changed.connect(self.observe_cam_pos_changed)
        self.vm.camera_rotation_changed.connect(self.observe_cam_rot_changed)
        self.vm.show_selected_changed.connect(self.observe_selected_changed)

        self._id.setText(self.vm.view_id())
        self.set_name(self.vm.name())
        self.set_camera_position(self.vm.camera_position())
        self.set_camera_rotation(self.vm.camera_rotation())
        self.set_head_color(self.vm.head_color())
        self.set_selected_status(self.vm.show_selected())


    def setup_ui(self):
        self._id = QLineEdit(self)
        self._id.setReadOnly(True)
        self._id.setText('NO ID')
        
        self._name = QLineEdit('Пользователь')
        self._name.textChanged.connect(self.handle_person_name_changed)
        self._name.returnPressed.connect(self.handle_person_name_changed)

        self._camera_pos_x = QDoubleSpinBox(self)
        self._camera_pos_y = QDoubleSpinBox(self)
        self._camera_pos_z = QDoubleSpinBox(self)

        self._camera_pos_x.setRange(-10000, 10000)
        self._camera_pos_y.setRange(-10000, 10000)
        self._camera_pos_z.setRange(-10000, 10000)

        self._camera_pos_x.setSingleStep(0.05)
        self._camera_pos_y.setSingleStep(0.05)
        self._camera_pos_z.setSingleStep(0.05)

        self._camera_pos_x.valueChanged.connect(self.handle_some_cam_pos_changed)
        self._camera_pos_y.valueChanged.connect(self.handle_some_cam_pos_changed)
        self._camera_pos_z.valueChanged.connect(self.handle_some_cam_pos_changed)

        self._camera_pos_x.setDecimals(3)
        self._camera_pos_y.setDecimals(3)
        self._camera_pos_z.setDecimals(3)

        self._camera_rot_x = QDoubleSpinBox(self)
        self._camera_rot_y = QDoubleSpinBox(self)
        self._camera_rot_z = QDoubleSpinBox(self)

        self._camera_rot_x.setRange(-10000, 10000)
        self._camera_rot_y.setRange(-10000, 10000)
        self._camera_rot_z.setRange(-10000, 10000)

        self._camera_rot_x.valueChanged.connect(self.handle_some_cam_rot_changed)
        self._camera_rot_y.valueChanged.connect(self.handle_some_cam_rot_changed)
        self._camera_rot_z.valueChanged.connect(self.handle_some_cam_rot_changed)

        self._camera_rot_x.setDecimals(3)
        self._camera_rot_y.setDecimals(3)
        self._camera_rot_z.setDecimals(3)

        self._color_widget_placeholder = QWidget()
        self._color_widget_placeholder.setMinimumSize(QSize(360, 200))
        self._color_widget_placeholder.setMaximumSize(QSize(360, 200))
        self._color_picker = ColorPicker(self._color_widget_placeholder, rgb=(220, 20, 137))
        self._color_picker.colorChanged.connect(self.handle_selected_color_changed)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Пользователь #'))
        hbox.addWidget(self._id)
        vbox.addLayout(hbox)

        grid = QGridLayout()
        vbox.addLayout(grid)
        
        self.remove_btn = QPushButton(self)
        self.remove_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.remove_btn.setText('Удалить')
        self.remove_btn.clicked.connect(self.handle_remove_clicked)
        self.select_btn = QPushButton(self)
        self.select_btn.clicked.connect(self.handle_select_clicked)
        self.select_btn.setText('Подсветить')

        grid.addWidget(self.select_btn, 0, 0)
        grid.addWidget(self.remove_btn, 0, 1)

        grid.addWidget(QLabel('Имя'), 1, 0)
        grid.addWidget(self._name, 1, 1)

        grid.addWidget(QLabel('Позиция камеры'), 2, 0)
        cam_pos_grid = QGridLayout()
        cam_pos_grid.addWidget(QLabel('x'), 0, 0)
        cam_pos_grid.addWidget(QLabel('y'), 0, 1)
        cam_pos_grid.addWidget(QLabel('z'), 0, 2)
        cam_pos_grid.addWidget(self._camera_pos_x, 1, 0)
        cam_pos_grid.addWidget(self._camera_pos_y, 1, 1)
        cam_pos_grid.addWidget(self._camera_pos_z, 1, 2)
        grid.addLayout(cam_pos_grid, 2, 1)

        grid.addWidget(QLabel('Вращение камеры'), 3, 0)
        cam_rot_grid = QGridLayout()
        cam_rot_grid.addWidget(QLabel('x'), 0, 0)
        cam_rot_grid.addWidget(QLabel('y'), 0, 1)
        cam_rot_grid.addWidget(QLabel('z'), 0, 2)
        cam_rot_grid.addWidget(self._camera_rot_x, 1, 0)
        cam_rot_grid.addWidget(self._camera_rot_y, 1, 1)
        cam_rot_grid.addWidget(self._camera_rot_z, 1, 2)
        grid.addLayout(cam_rot_grid, 3, 1)

        grid.addWidget(QLabel('Цвет пользователя'), 4, 0)
        grid.addWidget(self._color_widget_placeholder, 4, 1)

        self.setLayout(vbox)

    @Slot()
    def handle_select_clicked(self):
        self.vm.toggle_show_selected()

    @Slot()
    def handle_remove_clicked(self):
        self.vm.remove_element( )

    @Slot(bool)
    def observe_selected_changed(self, val:bool):
        self.set_selected_status(val)
        
    def set_selected_status(self, is_selected:bool):
        self.select_btn.setText('Убрать подсветку' if is_selected else 'Подсветить')
    
    @Slot()
    def handle_selected_color_changed(self):
        self.vm.set_head_color(QColor(*cast(tuple,self._color_picker.getRGB())))
    
    @Slot(QColor)
    def observe_head_color_changed(self, color:QColor):
        self.set_head_color(color)

    def set_head_color(self, color:QColor):
        rgb = cast(tuple, color.getRgb())[:3]
        if self._color_picker.getRGB() != rgb:
            self._color_picker.setRGB(rgb)

    @Slot(float)
    def handle_some_cam_pos_changed(self, val):
        x, y, z = self._camera_pos_x.value(), self._camera_pos_y.value(), self._camera_pos_z.value()
        self.vm.set_camera_position(QVector3D(x, y, z))

    def set_camera_position(self, pos:QVector3D):
        if self._camera_pos_x.value() != pos.x():
            self._camera_pos_x.setValue(pos.x())
        if self._camera_pos_y.value() != pos.y():
            self._camera_pos_y.setValue(pos.y())
        if self._camera_pos_z.value() != pos.z():
            self._camera_pos_z.setValue(pos.z())

    def set_camera_rotation(self, rot:QQuaternion):
        eul = rot.toEulerAngles()
        x = eul.x()
        y = eul.y()
        z = eul.z()
        if self._camera_rot_x.value() != x:
            self._camera_rot_x.setValue(x)
        if self._camera_rot_y.value() != y:
            self._camera_rot_y.setValue(y)
        if self._camera_rot_z.value() != z:
            self._camera_rot_z.setValue(z)

    @Slot(QVector3D)
    def observe_cam_pos_changed(self, pos:QVector3D):
        self.set_camera_position(pos)

    @Slot(float)
    def handle_some_cam_rot_changed(self, val):
        x, y, z = self._camera_rot_x.value(), self._camera_rot_y.value(), self._camera_rot_z.value()
        self.vm.set_camera_rotation(QQuaternion.fromEulerAngles(x, y, z))

    @Slot(QQuaternion)
    def observe_cam_rot_changed(self, rot:QQuaternion):
        self.set_camera_rotation(rot)

    @Slot()
    def handle_person_name_changed(self):
        self.vm.set_name(self._name.text())
    
    @Slot(str)
    def observe_person_name_changed(self, name):
        self.set_name(name)

    def set_name(self, name:str):
        if self._name.text()!=name:
            self._name.setText(name)

    @Slot()
    def observe_stop_editing(self):
        self.setEnabled(False)