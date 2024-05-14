from datetime import timedelta
from PySide6.QtCore import Slot
from PySide6.QtWidgets import  QWidget, QLabel, QSizePolicy, QVBoxLayout, QPushButton, QLineEdit, QDoubleSpinBox, QHBoxLayout, QGridLayout
from .person_options import PersonsForRuleSelectWidget
from .scene_obj_options import SceneObjsForRuleSelectWidget
from .vm import AttentionRuleConfigureWidgetVM
from dependency_injector.providers import Factory


class AttentionRuleConfigureWidget(QWidget):
    def __init__(self, 
                 vm:AttentionRuleConfigureWidgetVM) -> None:
        super().__init__()
        self.vm = vm
        self.setup_ui()

        self.vm.stop_editing.connect(self._observe_stop_editing)
        self.vm.visible_name_changed.connect(self._observe_visible_name_changed)
        self.vm.show_selected_changed.connect(self._observe_selected_changed)
        self.vm.seconds_without_attantion_changed.connect(self._observe_seconds_without_attention_changed)

        self.remove_btn.clicked.connect(self.vm.remove_element)

        self.set_visible_name(self.vm.visible_name())
        self._id.setText(self.vm.visible_id())
        self.set_selected(self.vm.show_selected())
        self.set_seconds_without_attention(self.vm.seconds_without_attention())
        
    def setup_ui(self):
        self._id = QLineEdit(self)
        self._id.setReadOnly(True)
        self._id.setText("NO ID")
        
        self._name = QLineEdit('Правило наблюдения')
        self._name.textChanged.connect(self.handle_name_changed)
        self._name.returnPressed.connect(self.handle_name_changed)
        
        
        self._time_without_attention = QDoubleSpinBox(self)
        self._time_without_attention.setRange(0, 3600)
        self._time_without_attention.setDecimals(0)
        self._time_without_attention.setValue(60)
        self._time_without_attention.setSuffix(' секунд')
        self._time_without_attention.valueChanged.connect(self.handle_time_without_attention_changed)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Правило наблюдения #'))
        hbox.addWidget(self._id)
        vbox.addLayout(hbox)

        grid = QGridLayout()
        vbox.addLayout(grid)
        
        self.select_btn = QPushButton(self)
        self.select_btn.clicked.connect(self.handle_select_clicked)
        self.select_btn.setText('Подсветить')
        self.remove_btn = QPushButton(self)
        self.remove_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.remove_btn.setText('Удалить')

        grid.addWidget(self.select_btn, 0, 0)
        grid.addWidget(self.remove_btn, 0, 1)

        grid.addWidget(QLabel('Название'), 1, 0)
        grid.addWidget(self._name, 1, 1)

        grid.addWidget(QLabel('Максимальное время\nбез наблюдения операторами'), 2, 0)
        grid.addWidget(self._time_without_attention, 2, 1)
        
        self._select_persons_container = PersonsForRuleSelectWidget(self.vm.persons_in_rule_collection(),
                                                                       self.vm.persons_not_in_rule_collection())
        vbox.addWidget(self._select_persons_container)

        self._select_scene_objs_container = SceneObjsForRuleSelectWidget(self.vm.scene_objs_in_rule_collection(),
                                                                            self.vm.scene_objs_not_in_rule_collection())
        vbox.addWidget(self._select_scene_objs_container)
        self.setLayout(vbox)

    
    @Slot(float)
    def handle_time_without_attention_changed(self, val_sec:float):
        self.vm.set_seconds_without_attention(val_sec)

    def set_seconds_without_attention(self, sec:float):
        if self._time_without_attention.value()!= sec:
            self._time_without_attention.setValue(sec)

    @Slot(float)
    def _observe_seconds_without_attention_changed(self, sec:float):
        self.set_seconds_without_attention(sec)

    @Slot()
    def handle_select_clicked(self):
        self.vm.toggle_show_selected()

    def set_selected(self, val:bool):
        self.select_btn.setText('Убрать подсветку' if val else 'Подсветить')
    
    @Slot(bool)
    def _observe_selected_changed(self, val:bool):
        self.set_selected(val)
    
    @Slot()
    def handle_name_changed(self):
        self.vm.set_visible_name(self._name.text())

    def set_visible_name(self, name:str):
        if self._name.text()!=name:
            self._name.setText(name)
    
    @Slot(str)
    def _observe_visible_name_changed(self, name:str):
        self.set_visible_name(name)

    @Slot()
    def _observe_stop_editing(self):
        self.setEnabled(False)