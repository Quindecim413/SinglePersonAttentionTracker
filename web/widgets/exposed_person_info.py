from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from common.collections.rules import RuleForPersonItem, RulesForPersonCollection
from common.widgets.info_rule import AttentionRuleInfoWidget
from common.widgets.options import ItemView, ItemViewFactory, ItemsCollectionView
from web.domain.exposed_person import ExposedPerson
from web.widgets.preview_exposed_person import ExposedPersonPreviewWidget


class RuleForPersonInfoWidgetFactory(ItemViewFactory[RuleForPersonItem]):
    def __call__(self, item: RuleForPersonItem) -> ItemView[RuleForPersonItem]:
        itemview = ItemView(item)
        itemview.set_content(AttentionRuleInfoWidget(item.rule()))
        return itemview


class ExposedPersonInfoWidget(QWidget):
    def __init__(self, 
                 exposed_person:ExposedPerson) -> None:
        super().__init__()
        self._exposed_person = exposed_person
        self._rules_for_person_collection = RulesForPersonCollection(self._exposed_person.person())
        self._rules_for_person_collection_view = ItemsCollectionView(self._rules_for_person_collection,
                                                                     RuleForPersonInfoWidgetFactory())

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        vbox.addWidget(ExposedPersonPreviewWidget(self._exposed_person))
        vbox.addWidget(QLabel('Правила:'))
        vbox.addWidget(self._rules_for_person_collection_view)
        
        self.setLayout(vbox)