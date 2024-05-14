from pathlib import Path
from dependency_injector import providers, containers
from common.containers import SceneContainer
from common.domain.interfaces import Person, SceneObj
from common.services.scene.project_data import AttentionProjectData
from common.vms.project_loading import ProjectImportVM
from common.widgets.preview_person import PersonPreviewWidget
from common.widgets.preview_proj_data import ProjectDataPreviewWidget
from common.widgets.preview_rule import AttentionRulePreviewWidget
from common.widgets.preview_scene_obj import SceneObjPreviewWidget

from configurator_app.configure_attention_rule.view import AttentionRuleConfigureWidget
from configurator_app.configure_attention_rule.vm import AttentionRuleConfigureWidgetVM
from configurator_app.configure_person.view import ConfigurePersonWidget
from configurator_app.configure_person.vm import PersonConfigureVM
from configurator_app.configure_project_data.view import ConfigureProjDataVM, ConfigureProjDataWidget
from configurator_app.configure_scene_obj.view import SceneObjConfigureWidget
from configurator_app.configure_scene_obj.vm import SceneObjConfigureVM

from configurator_app.main_window.view import ConfigureWindow
from configurator_app.main_window.vm import ConfigureWindowVM
from configurator_app.persons_page.preview_item import PersonItemFactory
from configurator_app.persons_page.view import ConfigurePersonsPage
from configurator_app.persons_page.vm import ConfigurePersonsPageVM
from configurator_app.projects_data_page.preview_item import ProjectDataItemFactory
from configurator_app.projects_data_page.view import ProjectsPage
from configurator_app.projects_data_page.vm import ProjectsPageVM
from configurator_app.rules_page.preview_item import RuleItemFactory
from configurator_app.rules_page.vm import ConfigureRulesPageVM
from configurator_app.rules_page.view import ConfigureRulesPage
from configurator_app.scene_objs_page.preview_item import SceneObjItemFactory
from configurator_app.scene_objs_page.view import ConfigureSceneObjsPage
from configurator_app.scene_objs_page.vm import ConfigureSceneObjsPageVM
from typing import Protocol

storage_dir = Path(__file__).parent.parent / 'docs' / 'configurator' / 'projects'



class ConfiguratorAppContainer(containers.DeclarativeContainer):
    scene = providers.Container(SceneContainer,
                                storage_dir=storage_dir)
    # project
    project_data_preview_widget = providers.Factory(ProjectDataPreviewWidget,
                                                    scene_initializer=scene.initializer)
    project_data_configure_vm = providers.Factory(ConfigureProjDataVM,
                                                  scene_initializer_service=scene.initializer,
                                                  projects_repo=scene.repo)
    @staticmethod
    def _project_data_configure_widget_factory(project_data:AttentionProjectData, vm_factory):
        return ConfigureProjDataWidget(vm=vm_factory(project_data))
    project_data_configure_widget_factory = providers.Callable(_project_data_configure_widget_factory, 
                                                               vm_factory=project_data_configure_vm.provider)

    # person
    person_preview_widget = providers.Factory(PersonPreviewWidget)
    # person_configure_widget = providers.Factory(ConfigurePersonWidget, vm=providers.Factory(PersonConfigureVM))
    @staticmethod
    def _person_obj_configure_widget_factory(person:Person, vm_factory):
        return ConfigurePersonWidget(vm=vm_factory(person))
    person_configure_widget_factory = providers.Callable(_person_obj_configure_widget_factory,
                                                         vm_factory=providers.Factory(PersonConfigureVM).provider)

    # scene obj
    scene_obj_preview_widget = providers.Factory(SceneObjPreviewWidget)
    # scene_obj_configure_widget = providers.Factory(SceneObjConfigureWidget, vm=providers.Factory(SceneObjConfigureVM))
    @staticmethod
    def _scene_obj_configure_widget_factory(scene_obj:SceneObj, vm_factory):
        return SceneObjConfigureWidget(vm=vm_factory(scene_obj))
    scene_obj_configure_widget_factory = providers.Callable(_scene_obj_configure_widget_factory,
                                                            vm_factory=providers.Factory(SceneObjConfigureVM).provider)

    # rule 
    rule_preview_widget = providers.Factory(AttentionRulePreviewWidget)
    # rule_configure_widget = providers.Factory(AttentionRuleConfigureWidget,
    #                                           vm=providers.Factory(AttentionRuleConfigureWidgetVM))
    @staticmethod
    def _rule_configure_widget_factory(rule, vm_factory):
        return AttentionRuleConfigureWidget(vm=vm_factory(rule))
    rule_configure_widget_factory = providers.Callable(_rule_configure_widget_factory,
                                                       vm_factory=providers.Factory(AttentionRuleConfigureWidgetVM).provider)

    # data items
    project_data_item_factory = providers.Factory(ProjectDataItemFactory,
                                        preview_widget_factory=project_data_preview_widget.provider,
                                        configure_widget_factory=project_data_configure_widget_factory.provider)

    person_item_factory = providers.Factory(PersonItemFactory,
                                            preview_widget_factory=person_preview_widget.provider,
                                            configure_widget_factory=person_configure_widget_factory.provider)
    
    scene_obj_item_factory = providers.Factory(SceneObjItemFactory,
                                               preview_widget_factory=scene_obj_preview_widget.provider,
                                               configure_widget_factory=scene_obj_configure_widget_factory.provider)

    rule_item_factory = providers.Factory(RuleItemFactory,
                                          preview_widget_factory=rule_preview_widget.provider,
                                          configure_widget_factory=rule_configure_widget_factory.provider)
    
    proj_data_page_vm = providers.Factory(ProjectsPageVM,
                                          scene_initializer=scene.initializer,
                                          attention_projects_repo=scene.repo)
    persons_page_vm = providers.Factory(ConfigurePersonsPageVM)
    scene_objs_page_vm = providers.Factory(ConfigureSceneObjsPageVM)
    rules_page_vm = providers.Factory(ConfigureRulesPageVM)
    
    project_import_vm = providers.Factory(ProjectImportVM,
                                          scene_initializer=scene.initializer,
                                          projects_repo=scene.repo)

    projects_page = providers.Factory(ProjectsPage,
                                    vm=proj_data_page_vm,
                                    project_import_vm=project_import_vm,
                                    item_factory=project_data_item_factory)
    
    persons_page = providers.Factory(ConfigurePersonsPage,
                                     item_factory=person_item_factory)
    scene_objs_page = providers.Factory(ConfigureSceneObjsPage,
                                        item_factory=scene_obj_item_factory)
    attention_rules_page = providers.Factory(ConfigureRulesPage,
                                             item_factory=rule_item_factory)

    configure_window_vm = providers.Singleton(ConfigureWindowVM,
                                              scene_initializer_service=scene.initializer,
                                              persons_vm_factory=persons_page_vm.provider,
                                              scene_objs_vm_factory=scene_objs_page_vm.provider,
                                              attention_rules_vm_factory=rules_page_vm.provider)
    
    configure_window = providers.Singleton(ConfigureWindow,
                                           vm=configure_window_vm,
                                           scene_window=scene.render_main_window,
                                           projects_page=projects_page,
                                           configure_persons_page_factory=persons_page.provider,
                                           configure_scene_objs_page_factory=scene_objs_page.provider,
                                           configure_attention_rules_page_factory=attention_rules_page.provider)