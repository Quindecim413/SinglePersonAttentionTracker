from typing import Generic, Protocol, TypeVar, cast
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import  QWidget, QFrame, QSizePolicy,\
    QSplitter, QScrollArea, QVBoxLayout


from common.collections.observing_items import Item, ItemsCollection
from ..utils import clear_layout


_T = TypeVar('_T', bound=Item, contravariant=True) 
T = TypeVar('T', bound=Item)

class PreviewItem(QWidget, Generic[T]):
    requested_remove = Signal(QWidget)
    focused_in = Signal(QWidget)

    def __init__(self, 
                 item:T,
                 content_widget:QWidget,
                 parent=None) -> None:
        super().__init__(parent)
        self._item = item
        self._item.removed.connect(self._observe_item_removed)
        self._content_layout = QVBoxLayout()
        vbox = QVBoxLayout()
        vbox.addLayout(self._content_layout)
        self._separator = QFrame()
        self._separator.setLineWidth(2)
        self._separator.setFrameShape(QFrame.Shape.HLine)
        self._separator.setFrameShadow(QFrame.Shadow.Sunken)
        vbox.addWidget(self._separator)
        vbox.addStretch()
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setLayout(vbox)
        self._content_layout.addWidget(content_widget)

    def item(self):
        return self._item

    @Slot()
    def _observe_item_removed(self):
        self.setEnabled(False)
        self.remove_element()
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.focused_in.emit(self)
        return super().mousePressEvent(event)
    
    @Slot()
    def remove_element(self):
        self.requested_remove.emit(self)

    def make_expanded_widget(self) -> QWidget:
        raise NotImplementedError()

    def show_focused(self, focus:bool):
        if focus:
            self._separator.setStyleSheet('background-color: #8bc4fc;')
        else:
            self._separator.setStyleSheet('')


class ExpandedItem(QWidget, Generic[T]):
    requested_remove = Signal(QWidget)
    def __init__(self, 
                 item:T,
                 configure_widget:QWidget, 
                 parent=None) -> None:
        super().__init__(parent)
        self._item = item
        self._item.removed.connect(self._observe_item_removed)
        self._content_layout = QVBoxLayout()
        self._content_layout.addWidget(configure_widget)
        self._content_layout.addStretch(1)
        self.setLayout(self._content_layout)
    
    @Slot()
    def _observe_item_removed(self):
        self.setEnabled(False)
        self.requested_remove.emit(self)


class ItemViewFactory(Protocol, Generic[_T]):
    def create_preview_widget(self, item:_T) -> QWidget:
        ...
    
    def create_expanded_widget(self, item:_T) -> QWidget:
        ...



class PreviewExpandWidget(QWidget, Generic[T]):
    def __init__(self, 
                 collection:ItemsCollection[T],
                 item_factory:ItemViewFactory[T],
                 parent=None,) -> None:
        super().__init__(parent)
        self.setMinimumSize(600, 300)
        self.setup_ui()

        self.layout().setContentsMargins(0,0,0,0)
        self._collection = collection
        self._collection.item_added.connect(self._observe_item_added)
        self._item_factory = item_factory
        for item in self._collection.items():
            self._add_preview_item(self._make_preview_item(item))
    
    def set_controls(self, w:QWidget):
        clear_layout(self._controls_layout)
        self._controls_layout.addWidget(w)

    def setup_ui(self):
        # Create the splitter to hold the two columns
        self.splitter = QSplitter(self)

        # Left column container
        self._left_column_widget = QWidget()
        self._left_column_widget.setMinimumWidth(300)
        left_column_layout = QVBoxLayout(self._left_column_widget)
        left_column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._left_column_widget.setLayout(left_column_layout)
        self._left_column_widget.layout().setContentsMargins(0,0,0,0)

        # Non-scrollable button at the top of the left column
        self._controls_layout = QVBoxLayout()
        left_column_layout.addLayout(self._controls_layout)

        # Left scrollable area
        left_scroll_area = QScrollArea()
        left_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        left_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll_area.setWidgetResizable(True)

        left_widget_contents = QWidget()
        self._preview_items_layout = QVBoxLayout(left_widget_contents)
        self._preview_items_layout.addStretch(1)
        self._preview_items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._preview_items_layout.setContentsMargins(0,0,0,0)
        left_widget_contents.setLayout(self._preview_items_layout)
        
        left_scroll_area.setWidget(left_widget_contents)

        # Add the scroll area below the fixed button
        left_column_layout.addWidget(left_scroll_area)

        # Right scrollable area
        right_scroll_area = QScrollArea(self.splitter)
        right_scroll_area.setWidgetResizable(True)
        right_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.right_widget = QWidget()
        self.right_widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self._expanded_item_layout = QVBoxLayout(self.right_widget)
        self.right_widget.setMinimumWidth(400)
        self.right_widget.setLayout(self._expanded_item_layout)
        
        # Populate the right column with some content
        right_scroll_area.setWidget(self.right_widget)
        

        self.splitter.addWidget(self._left_column_widget)
        self.splitter.addWidget(right_scroll_area)


        
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        # Set the splitter as the central widget of the main window
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    def resizeEvent(self, event):
        # This ensures the right column takes all available space on resize
        self.splitter.setSizes([self._left_column_widget.width(), self.width()])
        # self.right_widget.resize(self.right_widget.sizeHint())

    @Slot(Item)
    def _observe_item_added(self, item:T):
        self._add_preview_item(self._make_preview_item(item))

    def _make_preview_item(self, item:T):
        preview_widget = self._item_factory.create_preview_widget(item)
        if not isinstance(preview_widget, QWidget):
            raise TypeError()
        return PreviewItem(item, preview_widget)

    def _make_expanded_item(self, item:T):
        expanded_widget = self._item_factory.create_expanded_widget(item)
        if not isinstance(expanded_widget, QWidget):
            raise TypeError() 
        return ExpandedItem(item, expanded_widget)

    def _add_preview_item(self, item:PreviewItem):
        assert isinstance(item, PreviewItem)
        item.focused_in.connect(self._handle_preview_item_focused_in)
        item.requested_remove.connect(self._preview_widget_requested_remove)
        self._preview_items_layout.insertWidget(0, item)
    
    @Slot(QWidget)
    def _preview_widget_requested_remove(self, w:QWidget):
        self._preview_items_layout.removeWidget(w)
        clear_layout(self._expanded_item_layout)
        w.setParent(None)
        w.deleteLater()

    @Slot(QWidget)
    def _configure_item_requested_remove(self, w):
        clear_layout(self._expanded_item_layout)

    @Slot(QWidget)
    def _handle_preview_item_focused_in(self, preview_item:PreviewItem[T]):
        clear_layout(self._expanded_item_layout)
        for child_ind in range(self._preview_items_layout.count()):
            child:PreviewItem=cast(PreviewItem, self._preview_items_layout.itemAt(child_ind).widget())
            if child:
                if preview_item != child:
                    child.show_focused(False)
        preview_item.show_focused(True)
        expanded_item = self._make_expanded_item(preview_item.item())
        expanded_item.requested_remove.connect(self._configure_item_requested_remove)
        self._expanded_item_layout.addWidget(expanded_item)
    
    