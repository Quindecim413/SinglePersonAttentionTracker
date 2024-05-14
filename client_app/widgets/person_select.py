from typing import Any, Generic, Protocol, Type, TypeVar
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QFrame, QWidget, QToolButton, QVBoxLayout, QHBoxLayout, QButtonGroup, QRadioButton, QAbstractButton, QPushButton, QLabel
from common.collections.persons import SelectedPersonCollection, SelectedPersonItem, AvailablePersonItem, AvailablePersonsCollection
from common.domain.interfaces import Person
from common.widgets.options import AvailableItemViewFactory, ItemView, SelectItemsContainer, SelectedItemViewFactory


class PersonWidgetFactory(Protocol):
    def __call__(self, person:Person) -> QWidget:
        ...

class ExpandedPersonWidgetFactory(PersonWidgetFactory):
    ...

class ShortPersonWidgetFactory(PersonWidgetFactory):
    ...


class AvailablePersonOptionItem(ItemView[AvailablePersonItem]):
    def __init__(self, 
                 person_item:AvailablePersonItem,
                 factory:PersonWidgetFactory) -> None:
        super().__init__(person_item)
        self.person_item = person_item
        self.person_item.is_active_changed.connect(self._observe_is_active_changed)
        self.select_btn = QPushButton()
        self.select_btn.setCheckable(True)
        self.select_btn.clicked.connect(self._select_btn_clicked)
        content = factory(self.person_item.person())
        hbox = QHBoxLayout()
        hbox.addWidget(content)
        hbox.addWidget(self.select_btn)
        w = QWidget()
        w.setLayout(hbox)
        self.set_content(w)
        self.set_active(self.person_item.is_selected())

    @Slot()
    def _select_btn_clicked(self):
        self.person_item.make_active()

    @Slot(bool)
    def _observe_is_active_changed(self, is_loaded:bool):
        self.set_active(is_loaded)
        print(f'self.set_active({is_loaded=})')
        
    def set_active(self, is_active:bool):
        text = 'Выбрать' if is_active else 'Выбран'
        enabled = not is_active
        self.select_btn.setEnabled(enabled)
        self.select_btn.setText(text)
        self.select_btn.setChecked(is_active)


class SelectedPersonOptionItem(ItemView[SelectedPersonItem]):
    def __init__(self, 
                 person_item:SelectedPersonItem,
                 factory:PersonWidgetFactory) -> None:
        super().__init__(person_item)
        self.person_item = person_item
        self.person_item
        self.unselect_btn = QPushButton('Убрать')
        self.unselect_btn.clicked.connect(self._unselect_clicked)
        hbox = QHBoxLayout()
        hbox.addWidget(factory(self.person_item.person()))
        hbox.addWidget(self.unselect_btn)
        w = QWidget()
        w.setLayout(hbox)
        self.set_content(w)
    
    @Slot()
    def _unselect_clicked(self):
        self.person_item.make_not_active()


class SelectedPersonOptionItemFactory(SelectedItemViewFactory[SelectedPersonItem]):
    def __init__(self, person_widget_factory:ExpandedPersonWidgetFactory) -> None:
        super().__init__()
        self._person_widget_factory = person_widget_factory

    def __call__(self, item: SelectedPersonItem) -> ItemView[SelectedPersonItem]:
        return SelectedPersonOptionItem(item, self._person_widget_factory)


class AvailablePersonOptionItemFactory(AvailableItemViewFactory[AvailablePersonItem]):
    def __init__(self, person_widget_factory:ShortPersonWidgetFactory) -> None:
        super().__init__()
        self._person_widget_factory = person_widget_factory

    def __call__(self, item: AvailablePersonItem) -> ItemView[AvailablePersonItem]:
        return AvailablePersonOptionItem(item, self._person_widget_factory)


class PersonSelectionWidget(QWidget):
    def __init__(self, 
                 persons_collection:AvailablePersonsCollection,
                 active_person_collection:SelectedPersonCollection,
                 short_person_widget_factory:ShortPersonWidgetFactory,
                 expanded_person_widget_factory:ExpandedPersonWidgetFactory
                 ) -> None:
        super().__init__()
        
        self.select_options_container = SelectItemsContainer(active_person_collection,
                                                               persons_collection,
                                                               SelectedPersonOptionItemFactory(expanded_person_widget_factory),
                                                               AvailablePersonOptionItemFactory(short_person_widget_factory))
        
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Выбор активного пользователя'))
        vbox.addWidget(self.select_options_container)
        self.setLayout(vbox)