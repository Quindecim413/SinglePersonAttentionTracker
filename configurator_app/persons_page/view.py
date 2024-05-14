from PySide6.QtCore import Slot
from PySide6.QtWidgets import  QWidget, QPushButton, QVBoxLayout
from common.widgets.preview_expand import ItemViewFactory, PreviewExpandWidget
from configurator_app.persons_page.preview_item import PersonItemFactory
from .vm import ConfigurePersonsPageVM


class ConfigurePersonsPage(QWidget):
    def __init__(self,
                 vm:ConfigurePersonsPageVM,
                 item_factory:PersonItemFactory,
                 parent=None,) -> None:
        super().__init__(parent)
        self.vm = vm

        self.setMinimumSize(500, 500)

        self.preview_configure_widget = PreviewExpandWidget(self.vm.persons_collection(),
                                                            item_factory)
        
        self.setup_ui()

    
    def setup_ui(self):
        create_person_button = QPushButton("Добавить пользователя")
        create_person_button.clicked.connect(self.add_person_clicked)
        self.preview_configure_widget.set_controls(create_person_button)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_configure_widget)
        self.setLayout(vbox)
    
    @Slot()
    def add_person_clicked(self):
        self.vm.create_person()