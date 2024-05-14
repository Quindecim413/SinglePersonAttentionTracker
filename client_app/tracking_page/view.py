from functools import partial
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, Slot, QObject, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QStackedWidget, QButtonGroup, QTabWidget, QScrollArea
from client_app.tracking_page.vm import TrackingPageVM
from common.collections.persons import SelectedPersonItem
from common.collections.rules import RuleForPersonItem
from common.collections.scene_objs import SceneObjForPersonItem
from common.widgets.options import ItemView, ItemViewFactory, ItemsCollectionView



class SelectedPersonViewItemFactory(ItemViewFactory[SelectedPersonItem]):
    ...

class SceneObjForPersonItemViewFactory(ItemViewFactory[SceneObjForPersonItem]):
    ...

class RuleForPersonItemViewFactory(ItemViewFactory[RuleForPersonItem]):
    ...


class TrackingPage(QWidget):
    def __init__(self,
                 vm:TrackingPageVM,
                 selected_person_view_item_view_factory:SelectedPersonViewItemFactory,
                 scene_obj_for_person_item_view_factory:SceneObjForPersonItemViewFactory,
                 rule_for_person_item_view_factory:RuleForPersonItemViewFactory
                 ) -> None:
        super().__init__()
        self._vm = vm
        self._selected_person_view_item_view_factory = selected_person_view_item_view_factory
        self._scene_obj_for_person_item_view_factory = scene_obj_for_person_item_view_factory
        self._rule_for_person_item_view_factory = rule_for_person_item_view_factory

        self._vm.show_no_person_selected_changed.connect(self._observe_no_person_selected_changed)

        vbox = QVBoxLayout()

        self.nobody_selected_lbl = QLabel('Никто не выбран')
        self.selected_person_collection_view = ItemsCollectionView(self._vm.selected_person_collection(),
                                                                   self._selected_person_view_item_view_factory)
        
        self.selected_person_collection_view.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self._scene_objs_for_selected_person_collection_view = ItemsCollectionView(self._vm.scene_objs_for_active_person_collection(),
                                                                   self._scene_obj_for_person_item_view_factory)
        

        self._rules_for_selected_person_collection_view = ItemsCollectionView(self._vm.rules_for_active_person_collection(),
                                                                   self._rule_for_person_item_view_factory)

        


        self._tab_widget = QTabWidget()
        self._tab_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._tab_widget.addTab(self._scene_objs_for_selected_person_collection_view, 'Объекты сцены')
        self._tab_widget.addTab(self._rules_for_selected_person_collection_view, 'Правила наблюдения')
        # self._tab_widget.addTab(self._scene_objs_for_selected_person_collection_view, 'Объекты сцены')
        # self._tab_widget.addTab(self._rules_for_selected_person_collection_view, 'Правила наблюдения')
        self._tab_widget.setCurrentIndex(0)

        vbox.addWidget(QLabel('Выбранный оператор'), 0)
        vbox.addWidget(self.nobody_selected_lbl, 0)
        vbox.addWidget(self.selected_person_collection_view, 0)
        vbox.addWidget(self._tab_widget, 1)
        vbox.setContentsMargins(0,0,0,0)


        w = QWidget()
        w.setLayout(vbox)

        scroll_page = QScrollArea()
        scroll_page.setWidgetResizable(True)
        scroll_page.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_page.setWidget(w)
        main_vbox = QVBoxLayout()
        main_vbox.addWidget(scroll_page)
        main_vbox.setContentsMargins(0,0,0,0)
        self.setLayout(main_vbox)

    @Slot(bool)
    def _observe_no_person_selected_changed(self, nobody_selected:bool):
        self.nobody_selected_lbl.setVisible(nobody_selected)
