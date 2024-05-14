from pathlib import Path
from typing import Any, Callable, Protocol, TypeAlias
from common.collections.persons_in_rule import BasePersonsCollection, PersonItem
from common.domain.interfaces import Person
from common.widgets.options import ItemView, ItemViewFactory, ItemsCollectionView
from common.widgets.preview_person import PersonPreviewWidget
from .in_and_not_options import InRuleAndNotItemsContainer
from .vm import PersonsInRuleCollection, PersonsNotInRuleCollection
# from ..container import ConfiguratorAppContainer
from dependency_injector.providers import Factory
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Slot
from PySide6.QtGui import QPixmap



class PersonItemView(ItemView[PersonItem]):
    def __init__(self, 
                 item:PersonItem,
                 ) -> None:
        super().__init__(item, draggable=True)
        self.set_content(PersonPreviewWidget(item.person()))


class PersonItemViewFactory(ItemViewFactory[PersonItem]):
    ...

class PersonInRuleOption(PersonItemView):
    def make_mime_pixmap(self):
        return QPixmap(Path(__file__).parent.parent/'src/remove-person.png')


class PersonNotInRuleOption(PersonItemView):
    def make_mime_pixmap(self):
        return QPixmap(Path(__file__).parent.parent/'src/add-person.png')

class PersonInRuleOptionItemFactory(PersonItemViewFactory):
    def __call__(self, item: PersonItem) -> ItemView:
        return PersonInRuleOption(item)
    

class PersonNotInRuleOptionItemFactory(PersonItemViewFactory):
    def __call__(self, item: PersonItem) -> ItemView:
        return PersonNotInRuleOption(item)
    

class PersonsForRuleSelectWidget(QWidget):
    def __init__(self, 
                 persons_in_rule:PersonsInRuleCollection,
                 persons_not_in_rule:PersonsNotInRuleCollection,
                 ) -> None:
        super().__init__()
        self.in_options_view = ItemsCollectionView(persons_in_rule, PersonInRuleOptionItemFactory())
        self.not_in_options_view = ItemsCollectionView(persons_not_in_rule, PersonNotInRuleOptionItemFactory())
        self.options = InRuleAndNotItemsContainer(self.in_options_view, self.not_in_options_view)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Перетащите пользователей в соответствующие колонки'))
        vbox.addWidget(self.options)
        self.setLayout(vbox)