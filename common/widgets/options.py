from pathlib import Path
from typing import Generic, TypeVar, cast
from typing import Any, Protocol
from PySide6.QtCore import Qt, Slot, Signal, QSize, QMimeData
from PySide6.QtGui import QCloseEvent, QMouseEvent, QPainter, QColor,QBrush, QDrag, QPixmap, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QToolBar, QLabel, QFrame, QApplication,\
    QSplitter, QScrollArea, QVBoxLayout, QPushButton, QLineEdit, QDoubleSpinBox, QSpinBox, QGridLayout, QHBoxLayout, QToolButton
from common.collections.observing_items import Item, ItemsCollection

from common.utils import clear_layout


T = TypeVar('T', bound=Item)

class ItemView(QFrame, Generic[T]):
    def __init__(self, item:T, draggable=False, parent=None) -> None:
        super().__init__(parent)
        self._item = item
        self._item.removed.connect(self._item_removed)
        self.drag_start_position = None
        self.draggable = draggable

        self._content_layout = QVBoxLayout()
        self._content_layout.addWidget(QLabel('Здесь будет что-то'))
        vbox = QVBoxLayout()
        self._separator = QFrame()
        self._separator.setLineWidth(2)
        self._separator.setFrameShape(QFrame.Shape.HLine)
        self._separator.setFrameShadow(QFrame.Shadow.Sunken)
        vbox.addLayout(self._content_layout)
        vbox.addWidget(self._separator)
        vbox.addStretch()
        self.setLayout(vbox)

    def item(self):
        return self._item

    def set_content(self, w:QWidget):
        clear_layout(self._content_layout)
        self._content_layout.addWidget(w)
        self._content_layout.addStretch()
        self.adjustSize()

    requested_remove = Signal(QWidget)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not self.draggable:
            return
        
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if self.drag_start_position is None:
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        mime = self._item.make_mimedata()
        if not mime:
            return
        pixmap = self.make_mime_pixmap()
        if not pixmap:
            pixmap = QPixmap(Path(__file__).parent / 'src/broken-image.png')

        drag = QDrag(self)
        drag.setPixmap(pixmap)
        drag.setMimeData(mime)

        drag.exec_(Qt.DropAction.MoveAction)

    def make_mime_pixmap(self)->QPixmap|None:
        return None
    
    @Slot()
    def _item_removed(self):
        self.requested_remove.emit(self)

I = TypeVar('I', bound=Item)
class ItemViewFactory(Protocol[I]):
    def __call__(self, item:I,) -> ItemView[I]:
        ...

class ItemsCollectionView(QFrame, Generic[I]):
    def __init__(self, 
                 collection:ItemsCollection[I]|None=None,
                 view_item_factory:ItemViewFactory[I]|None=None,
                 parent=None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setLineWidth(1)
        self._layout = QVBoxLayout()
        self._layout.addStretch(1)
        self._layout.setContentsMargins(1,1,1,1)
        self._layout.setSpacing(1)
        self.setLayout(self._layout)
        self.setStyleSheet('background-color: #e0e0e0;')
        self.setMinimumHeight(100)
        self.setAcceptDrops(True)
        self._items_collection:ItemsCollection[I]|None = None
        self._item_view_factory:ItemViewFactory[I]|None=None

        self.set_view_item_factory(view_item_factory)
        self.set_collection(collection)

    def set_collection(self, collection:ItemsCollection[I]|None):
        if self._items_collection is not None:
            self._items_collection.disconnect(self)
        
        self._items_collection = collection
        if self._items_collection is not None:
            self._items_collection.item_added.connect(self._observe_collection_item_added)
        self.__try_populate_layout()

    def set_view_item_factory(self, view_item_factory:ItemViewFactory[I]|None):
        self._item_view_factory = view_item_factory
        self.__try_populate_layout()

    def __try_populate_layout(self):
        self.__clear_layout()
        if self._items_collection is None:
            return
        
        for item in self._items_collection.items():
            self._add_item(item)

    def __clear_layout(self):
        for w in list(self._layout.children()):
            if isinstance(w, ItemView):
                self.__remove_item_view(w)

    def _add_item(self, item:I):
        assert isinstance(item, Item)
        if self._item_view_factory:
            item_view = self._item_view_factory(item)
            self._layout.insertWidget(0, item_view)
            item_view.requested_remove.connect(self._handle_option_remove)
            self.resize(self.sizeHint())
    @Slot(Item)
    def _observe_collection_item_added(self, item:I):
        if self._item_view_factory:
            self._add_item(item)

    @Slot(QWidget)
    def _handle_option_remove(self, w:QWidget):
        self.__remove_item_view(w)
    
    def __remove_item_view(self, w:QWidget):
        self._layout.removeWidget(w)
        w.deleteLater()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        if self._items_collection is not None:
            self._items_collection.handle_mimedata(event.mimeData())
        # self.mimedata_accepted.emit(event.mimeData())


class ItemsCollectionsMultiView(QWidget):
    def __init__(self, options_contrainers:list[ItemsCollectionView], parent=None) -> None:
        super().__init__(parent)
        self._options_containers = list(options_contrainers)
        hbox = QHBoxLayout()
        for c in self._options_containers:
            hbox.addWidget(c)
        
        self.setLayout(hbox)



I1 = TypeVar('I1', bound=Item, contravariant=True)
I2 = TypeVar('I2', bound=Item, contravariant=True)

class AvailableItemViewFactory(ItemViewFactory[I]):
        ...

class SelectedItemViewFactory(ItemViewFactory[I]):
        ...


class SelectItemsContainer(QFrame, Generic[I1, I2]):
    def __init__(self,
                 selected_items_collection:ItemsCollection[I1],
                 available_items_collection:ItemsCollection[I2],
                 selected_item_factory:SelectedItemViewFactory[I1],
                 available_item_factory:AvailableItemViewFactory[I2]
                 ) -> None:
        super().__init__()
        self.selected_items_collection = selected_items_collection
        self.selected_item_factory = selected_item_factory

        self.available_items_collection = available_items_collection
        self.available_item_factory = available_item_factory

        self._selected_options_container = ItemsCollectionView(self.selected_items_collection, self.selected_item_factory)
        self._available_options_container = ItemsCollectionView(self.available_items_collection, self.available_item_factory)
        self.setup_ui()

    def setup_ui(self):
        self._selected_options_container.setMinimumHeight(50)

        self.selected_title = QLabel('Выбрано')

        self.toggle_button = QToolButton()
        self.toggle_button.setText('Выберите из доступных вариантов')
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.pressed.connect(self._expand_pressed)
        
        self.toggle_frame = QFrame()
        self.toggle_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.toggle_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.content_area = QVBoxLayout()
        self.toggle_frame.setLayout(self.content_area)
        self.content_area.setContentsMargins(0, 0, 0, 0)

        self.content_area.addWidget(self._available_options_container)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.selected_title)
        self.main_layout.addWidget(self._selected_options_container)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.toggle_frame)
        # self.main_layout.addLayout(self.content_area)

        self.setLayout(self.main_layout)
        self.toggle_frame.setVisible(False)

    def _expand_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)
        self.toggle_frame.setVisible(checked)
        # self.content_area.parentWidget().setVisible(checked)

    def set_options_title(self, title:str):
        self.toggle_button.setText(title)

    def set_selected_item_title(self, title:str):
        self.selected_title.setText(title)