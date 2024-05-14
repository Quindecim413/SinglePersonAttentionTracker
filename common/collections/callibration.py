
from common.collections.observing_items import Item, ItemsCollection
from common.dtos.calibration import CallibrationRecord


class CallibrationRecordItem(Item):
    def __init__(self, record:CallibrationRecord) -> None:
        super().__init__()
        self._record = record

    def record(self):
        return self._record

    def remove(self):
        self.remove_item()


class CallibrationRecordsCollection(ItemsCollection[CallibrationRecordItem]):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
    
    def add_record(self, record:CallibrationRecord):
        if not isinstance(record, CallibrationRecord):
            raise TypeError()
        self.add_item(CallibrationRecordItem(record))

    def reset(self):
        self.clear()

    def records(self):
        return [i.record() for i in self.items()]