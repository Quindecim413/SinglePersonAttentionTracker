from typing import Callable, Protocol
from PySide6.QtWidgets import QWidget
from dependency_injector.providers import Factory
from common.collections.rules import RuleInSceneItem
from common.domain.interfaces import AttentionRule

from common.widgets.preview_expand import ItemViewFactory, PreviewItem
from common.widgets.preview_rule import AttentionRulePreviewWidget
from configurator_app.configure_attention_rule.view import AttentionRuleConfigureWidget


class PreviewRuleWidgetFactory(Protocol):
    def __call__(self, rule:AttentionRule) -> QWidget:
        ...

class ConfigureRuleWidgetFactory(Protocol):
    def __call__(self, rule:AttentionRule) -> QWidget:
        ...


class RuleItemFactory(ItemViewFactory[RuleInSceneItem]):
    def __init__(self,
                 preview_widget_factory:PreviewRuleWidgetFactory,
                 configure_widget_factory:ConfigureRuleWidgetFactory,) -> None:
        super().__init__()
        self.preview_widget_factory = preview_widget_factory
        self.configure_widget_factory = configure_widget_factory

    def create_preview_widget(self, item: RuleInSceneItem) -> QWidget:
        return self.preview_widget_factory(item.rule())
    
    def create_expanded_widget(self, item: RuleInSceneItem) -> QWidget:
        return self.configure_widget_factory(item.rule())