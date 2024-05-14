from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout
from common.widgets.preview_expand import ItemViewFactory, PreviewExpandWidget
from configurator_app.rules_page.preview_item import RuleItemFactory
from configurator_app.rules_page.vm import ConfigureRulesPageVM



class ConfigureRulesPage(QWidget):
    def __init__(self, 
                 vm:ConfigureRulesPageVM,
                 item_factory:RuleItemFactory
                 ) -> None:
        super().__init__()
        self.vm = vm
        self.setMinimumSize(500, 500)
        self.preview_configure_widget = PreviewExpandWidget(self.vm.attention_rules_collection(),
                                                            item_factory)
        self.setup_ui()
    
    @Slot()
    def add_rule_clicked(self):
        self.vm.create_attention_rule()
    
    def setup_ui(self):        
        add_rule_button = QPushButton("Создать правило")
        add_rule_button.clicked.connect(self.add_rule_clicked)
        self.preview_configure_widget.set_controls(add_rule_button)
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_configure_widget)
        self.setLayout(vbox)
