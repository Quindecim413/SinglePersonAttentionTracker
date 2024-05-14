from PySide6.QtCore import QObject, Signal, QMimeData, Slot, QModelIndex

from abc import abstractmethod
from typing import Any, Generic, Optional, TypeVar, cast


class Item(QObject):
    removed = Signal()
    def __init__(self) -> None:
        super().__init__()
        self.__observing_collection:ItemsCollection|None = None
        self._item_content_removed = False

    @property
    def _collection(self):
        return self.__observing_collection
    
    @_collection.setter
    def _collection(self, collection:Optional['ItemsCollection']):
        if self._collection is not None and collection is not None:
            raise ValueError('Can not add item which already belongs to collection')
        if collection is None:
            self.__observing_collection = None
        else:
            if not isinstance(collection, ItemsCollection):
                raise TypeError(f'Expected {ItemsCollection.__class__}, got {type(collection)}')
        self.__observing_collection = collection

    def make_mimedata(self) -> QMimeData|None:
        return None
    
    @Slot()
    def remove_item(self):
        if self.__observing_collection != None:
            self.__observing_collection.remove_item(self)
        
        self._item_content_removed = True
    
    def _notify_removed(self):
        self.removed.emit()
    
    def content_removed(self) -> bool:
        return self._item_content_removed


I = TypeVar('I', bound=Item)


class ItemsCollection(QObject, Generic[I]):
    item_added = Signal(Item)
    item_removed = Signal(Item)
    items_changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._items:list[I] = list()

    def items(self) -> list[I]:
        return list(self._items)
    
    def handle_mimedata(self, mimedata:QMimeData):
        return
    
    def __len__(self) -> int:
        return len(self._items)

    def clear(self):
        for item in self._items:
            self.remove_item(item)

    def add_item(self, item:I):
        if not isinstance(item, Item):
            raise TypeError(f'Expected {Item}, recieved {type(item)}')
        if item in self._items:
            return
        
        if item._item_content_removed:
            return
        
        if item._collection is not None:
            item._collection.remove_item(item)
        
        item._collection = self
        self._items.append(item)
        self.item_added.emit(item)
        self.items_changed.emit()

    def remove_item(self, item:Item):
        if isinstance(item, Item) and item in self._items:
            self._items.remove(cast(I, item))
            item._collection = None
            item._notify_removed()
            self.item_removed.emit(item)
            self.items_changed.emit()