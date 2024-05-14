from datetime import date, datetime, timedelta
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QSizePolicy, QWidget, QLabel, QPushButton, QHBoxLayout, QDoubleSpinBox, QGridLayout, QVBoxLayout, QLineEdit, QTabWidget, QProgressBar

from common.collections.persons_in_rule import PersonItem, PersonsInRuleCollection
from common.collections.scene_obj_in_rule import SceneObjItem, SceneObjsInRuleCollection
from common.domain.interfaces import AttentionRule
from common.widgets.options import ItemView, ItemViewFactory, ItemsCollectionView
from common.widgets.preview_person import PersonPreviewWidget
from common.widgets.preview_scene_obj import SceneObjPreviewWidget


class PersonItemViewFactory(ItemViewFactory[PersonItem]):
    def __call__(self, item: PersonItem) -> ItemView[PersonItem]:
        item_view = ItemView(item)
        item_view.set_content(PersonPreviewWidget(item.person()))
        return item_view

class SceneObjItemViewFactory(ItemViewFactory[SceneObjItem]):
    def __call__(self, item: SceneObjItem) -> ItemView[SceneObjItem]:
        item_view = ItemView(item)
        item_view.set_content(SceneObjPreviewWidget(item.scene_obj()))
        return item_view


pb_error_stylesheet = """
    QProgressBar::chunk {
        background-color: red;
    }
"""

class AttentionRuleInfoWidget(QWidget):
    def __init__(self, 
                 attention_rule:AttentionRule,) -> None:
        super().__init__()
        self._rule = attention_rule
        self._person_in_rule = PersonsInRuleCollection(self._rule)
        self._scene_objs_in_rule = SceneObjsInRuleCollection(self._rule)
        self._person_item_view_factory = PersonItemViewFactory()
        self._scene_obj_item_view_factory = SceneObjItemViewFactory()
        self.setup_ui()

        self._rule.removed_from_scene.connect(self._observe_removed)
        self._rule.element_name_changed.connect(self._observe_name_changed)
        self._rule.is_selected_changed.connect(self._observe_selected_changed)
        # self._rule.last_refresh_timestamp_changed.connect(self._observe_last_refresh_timestamp_changed)
        self._rule.without_attention_timedelta_changed.connect(self._observe_without_attention_timedelta_changed)
        self._rule.scene().updated.connect(self._observe_scene_updated)
        self._set_visible_name(self._rule.element_name())
        self._id.setText(str(self._rule.element_id()))
        self._set_selected(self._rule.is_selected())
        self._update_progress()
        
    def setup_ui(self):
        self._id = QLineEdit(self)
        self._id.setReadOnly(True)
        self._id.setText("NO ID")
        
        self._name = QLabel('Правило наблюдения')
        self._name.setWordWrap(True)
        
        self._select_btn = QPushButton('')
        self._select_btn.setFixedSize(15, 15)
        self._select_btn.clicked.connect(self._toggle_selection_clicked)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self._select_btn)
        hbox.addWidget(QLabel('Правило наблюдения #'))
        hbox.addWidget(self._id)
        vbox.addLayout(hbox)

        grid = QGridLayout()
        vbox.addLayout(grid)
        
    

        vbox.addWidget(QLabel('Название'))
        vbox.addWidget(self._name)

        vbox.addWidget(QLabel('Время без наблюдения'))

        self._time_without_attention_progress_lbl = QLabel('?/? сек.')
        self._progress_to_error_progress_bar = QProgressBar()
        self._progress_to_error_progress_bar.setMinimum(0)
        self._progress_to_error_progress_bar.setMaximum(100)
        self._progress_to_error_progress_bar.setTextVisible(False)
        hbox = QHBoxLayout()
        hbox.addWidget(self._progress_to_error_progress_bar, 1)
        hbox.addWidget(self._time_without_attention_progress_lbl, 0)
        vbox.addLayout(hbox)

        persons_scene_objs_tabs = QTabWidget()
        
        self._persons_in_rule_view = ItemsCollectionView(self._person_in_rule,
                                                         self._person_item_view_factory)
        
        persons_scene_objs_tabs.addTab(self._persons_in_rule_view, 'Операторы')

        self._scene_objs_in_rule_view = ItemsCollectionView(self._scene_objs_in_rule,
                                                            self._scene_obj_item_view_factory)
        persons_scene_objs_tabs.addTab(self._scene_objs_in_rule_view, 'Объекты окружения')

        vbox.addWidget(persons_scene_objs_tabs)
        self.setLayout(vbox)

    # @Slot(datetime)
    # def _observe_last_refresh_timestamp_changed(self, last_refresh_timestamp:datetime):
    #     self._update_progress()

    @Slot()
    def _observe_scene_updated(self):
        self._update_progress()
    
    def _update_progress(self):
        # last_refresh_timestamp = self._rule.last_refresh_timestamp()
        timestamp = self._rule.scene().timer().now()
        without_attention_max_sec = self._rule.without_attention_timedelta().total_seconds()
        # print(f'{timestamp=}')
        # print(f'{self._rule.until_error_progress(last_refresh_timestamp)=}')
        progress_to_error = 1 - self._rule.until_error_progress(timestamp)
        time_until_error = self._rule.time_util_error(timestamp)
        # print(f'{timestamp=}, {time_until_error=}')
        if time_until_error is not None:
            seconds_passed_from_refresh = without_attention_max_sec - time_until_error.total_seconds()
        else:
            seconds_passed_from_refresh = float(0)

        if progress_to_error > 1:
            self._progress_to_error_progress_bar.setStyleSheet(pb_error_stylesheet)
        else:
            self._progress_to_error_progress_bar.setStyleSheet('')
        
        self._progress_to_error_progress_bar.setValue(int(progress_to_error*100))
        self._time_without_attention_progress_lbl.setText(f'{seconds_passed_from_refresh:.1f} / {without_attention_max_sec:.1f} сек.')

    @Slot(timedelta)
    def _observe_without_attention_timedelta_changed(self, time_without_attention:timedelta):
        self._update_progress()

    @Slot()
    def handle_select_clicked(self):
        self._rule.set_selected(not self._rule.is_selected())

    @Slot(bool)
    def _observe_selected_changed(self, selected:bool):
        self._set_selected(selected)
    
    def _set_selected(self, selected:bool):
        if selected:
            self._select_btn.setStyleSheet('background-color: #fcf403;')
        else:
            self._select_btn.setStyleSheet('')
    
    @Slot()
    def _toggle_selection_clicked(self):
        self._rule.set_selected(not self._rule.is_selected())


    def _set_visible_name(self, name:str):
        if self._name.text()!=name:
            self._name.setText(name)
    
    @Slot(str)
    def _observe_name_changed(self, name:str):
        self._set_visible_name(name)

    @Slot()
    def _observe_removed(self):
        self.setEnabled(False)