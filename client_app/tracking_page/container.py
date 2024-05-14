from dependency_injector import containers, providers
from PySide6.QtWidgets import QSizePolicy
from client_app.tracking_page.view import RuleForPersonItemViewFactory, SceneObjForPersonItemViewFactory, SelectedPersonViewItemFactory, TrackingPage
from client_app.tracking_page.vm import RulesForSelectedPersonCollection, SceneObjsForSelectedPersonCollection, TrackingPageVM
from common.collections.persons import SelectedPersonCollection, SelectedPersonItem
from common.collections.rules import RuleForPersonItem
from common.collections.scene_objs import SceneObjForPersonItem
from common.services.active_person import ActivePersonSelector
from common.services.active_work_state import ActiveWorkState
from common.widgets.info_rule import AttentionRuleInfoWidget
from common.widgets.options import ItemView
from common.widgets.preview_person import PersonPreviewWidget
from common.widgets.preview_scene_obj import SceneObjPreviewWidget


class SelectedPersonIVFactory(SelectedPersonViewItemFactory):
    def __call__(self, item: SelectedPersonItem) -> ItemView[SelectedPersonItem]:
        item_view = ItemView(item)
    #    item_view.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        content = PersonPreviewWidget(item.person())
        item_view.set_content(content)
        content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        return item_view


class SceneObjForPersonIVFactory(SceneObjForPersonItemViewFactory):
    def __call__(self, item: SceneObjForPersonItem) -> ItemView[SceneObjForPersonItem]:
        item_view = ItemView(item)
        content = SceneObjPreviewWidget(item.scene_obj())
        item_view.set_content(content)
        content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        return item_view


class RuleForPersonIVFactory(RuleForPersonItemViewFactory):
    def __call__(self, item: RuleForPersonItem) -> ItemView[RuleForPersonItem]:
        item_view = ItemView(item)
        item_view.set_content(AttentionRuleInfoWidget(item.rule()))
        return item_view


class TrackingPageContainer(containers.DeclarativeContainer):
    active_person_selector = providers.Dependency(instance_of=ActivePersonSelector)
    active_work_state = providers.Dependency(instance_of=ActiveWorkState)

    selected_person_collection = providers.Factory(SelectedPersonCollection,
                                                   active_person_selector=active_person_selector)
    
    rules_for_selected_person_collection = providers.Factory(RulesForSelectedPersonCollection,
                                                             active_work_state=active_work_state)
    
    scene_objs_for_selected_person_collection = providers.Factory(SceneObjsForSelectedPersonCollection,
                                                                  active_work_state=active_work_state)
    
    page_vm = providers.Factory(TrackingPageVM,
                                selected_person_collection=selected_person_collection,
                                scene_objs_for_selected_person_collection=scene_objs_for_selected_person_collection,
                                rules_for_selected_person_collection=rules_for_selected_person_collection)

    page = providers.Factory(TrackingPage,
                             vm=page_vm,
                             selected_person_view_item_view_factory=providers.Factory(SelectedPersonIVFactory),
                             scene_obj_for_person_item_view_factory=providers.Factory(SceneObjForPersonIVFactory),
                             rule_for_person_item_view_factory=providers.Factory(RuleForPersonIVFactory))