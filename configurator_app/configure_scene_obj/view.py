from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QDoubleSpinBox, QGridLayout, QHBoxLayout
from .vm import SceneObjConfigureVM


class SceneObjConfigureWidget(QWidget):
    def __init__(self, 
                 vm:SceneObjConfigureVM) -> None:
        super().__init__()
        self.vm = vm
        self.setup_ui()
        self.vm.stopped_editing.connect(self._handle_stop_editing)
        self.vm.name_changed.connect(self.observe_view_name_changed)
        self.vm.show_selected_changed.connect(self.observe_show_selected_changed)
        self.vm.keep_attention_seconds_changed.connect(self.observe_keep_attention_seconds_changed)
        self.id_.setText(self.vm.view_id())
        self.name.setText(self.vm.name())
        self.keep_attention_time.setValue(vm.keep_attention_seconds())
        self.set_selected_status(self.vm.show_selected())

    @Slot()
    def _handle_stop_editing(self):
        self.setEnabled(False)

    def setup_ui(self):
        self.id_ = QLineEdit(self)
        self.id_.setReadOnly(True)
        self.id_.setText('NO ID')
        
        self.name = QLineEdit('Объект сцены')
        self.name.textChanged.connect(self.handle_name_changed)
        self.name.returnPressed.connect(self.handle_name_changed)

        self.keep_attention_time = QDoubleSpinBox(self)
        self.keep_attention_time.setRange(0, 60)
        self.keep_attention_time.setDecimals(1)
        self.keep_attention_time.setSingleStep(0.1)
        self.keep_attention_time.setValue(3)
        self.keep_attention_time.setSuffix(' секунд')
        self.keep_attention_time.valueChanged.connect(self.handle_keep_attention_time_value_changed)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Объект сцены #'))
        hbox.addWidget(self.id_)
        vbox.addLayout(hbox)

        grid = QGridLayout()
        vbox.addLayout(grid)
        
        self.select_btn = QPushButton(self)
        self.select_btn.clicked.connect(self.handle_select_clicked)
        self.select_btn.setText('Подсветить')

        grid.addWidget(self.select_btn, 0, 0)

        grid.addWidget(QLabel('Название'), 1, 0)
        grid.addWidget(self.name, 1, 1)

        grid.addWidget(QLabel('Минимальное время\nудержания внимания оператора'), 2, 0)
        grid.addWidget(self.keep_attention_time, 2, 1)
        self.setLayout(vbox)
    
    @Slot(float)
    def handle_keep_attention_time_value_changed(self, val:float):
        self.vm.set_keep_attention_seconds(val)

    @Slot(float)
    def observe_keep_attention_seconds_changed(self, sec:float):
        self.keep_attention_time.setValue(sec)

    @Slot()
    def handle_select_clicked(self):
        self.vm.toggle_show_selected()

    @Slot(bool)
    def observe_show_selected_changed(self, val:bool):
        self.set_selected_status(val)
    
    def set_selected_status(self, val:bool):
        self.select_btn.setText('Убрать подсветку' if val else 'Подсветить')
    
    @Slot()
    def handle_name_changed(self):
        self.vm.set_name(self.name.text())
    
    @Slot(str)
    def observe_view_name_changed(self, name):
        if self.name.text()!=name:
            self.name.setText(name)