from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from common.widgets.options import ItemsCollectionsMultiView, ItemsCollectionView


class InRuleAndNotItemsContainer(QWidget):
    def __init__(self, 
                 in_rule_options:ItemsCollectionView,
                 not_in_rule_options:ItemsCollectionView
                 ) -> None:
        super().__init__()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignJustify)
        l1 = QLabel('Принадлежит правилу')
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l2 = QLabel('Не принадлежит правилу')
        l2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hbox.addWidget(l1, 1, Qt.AlignmentFlag.AlignCenter)
        hbox.addWidget(l2, 1, Qt.AlignmentFlag.AlignCenter)
        vbox.addLayout(hbox)

        self.multioptions = ItemsCollectionsMultiView([in_rule_options, not_in_rule_options])
        vbox.addWidget(self.multioptions)
        self.setLayout(vbox)
