from PySide6.QtCore import Slot, Signal, QObject
from common.collections.rules import RulesInSceneCollection
from common.domain.interfaces import AttentionRule, AttentionScene


class ConfigureRulesPageVM(QObject):
    def __init__(self, scene:AttentionScene) -> None:
        super().__init__()
        self._scene = scene
        self._rules_collection = RulesInSceneCollection(self._scene)

    def attention_rules_collection(self) -> RulesInSceneCollection:
        return self._rules_collection
    
    def create_attention_rule(self):
        self._rules_collection.create_rule()
