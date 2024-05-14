from __future__ import annotations
from PySide6.QtCore import QObject, Signal, Slot
from dependency_injector.providers import Factory
from common.services.scene.initializer import AttentionSceneInitializerService
from configurator_app.persons_page.vm import ConfigurePersonsPageVM
from configurator_app.rules_page.vm import ConfigureRulesPageVM
from configurator_app.scene_objs_page.vm import ConfigureSceneObjsPageVM


class ConfigureWindowVM(QObject):
    attention_scene_editable_changed = Signal(bool)

    def __init__(self,
                 scene_initializer_service:AttentionSceneInitializerService,
                 persons_vm_factory:Factory[ConfigurePersonsPageVM],
                 scene_objs_vm_factory:Factory[ConfigureSceneObjsPageVM],
                 attention_rules_vm_factory:Factory[ConfigureRulesPageVM]
                 ) -> None:
        super().__init__()
        self._scene_initializer_service = scene_initializer_service
        self._persons_vm_factory = persons_vm_factory
        self._scene_objs_vm_factory = scene_objs_vm_factory
        self._attention_rules_vm_factory = attention_rules_vm_factory
        self._scene_initializer_service.attention_project_changed.connect(self._handle_attention_project_changed)

    def attention_scene_elements_editable(self):
        return self._scene_initializer_service.has_initialized_project()

    def persons_window_vm(self):
        if p:= self._scene_initializer_service.project():
            return self._persons_vm_factory(p.scene())
        else:
            raise RuntimeError('scene is not initialized yet')

    def scene_objs_window_vm(self):
        if p:= self._scene_initializer_service.project():
            return self._scene_objs_vm_factory(p.scene())
        else:
            raise RuntimeError('scene is not initialized yet')

    def rules_window_vm(self):
        if p:= self._scene_initializer_service.project():
            return self._attention_rules_vm_factory(p.scene())
        else:
            raise RuntimeError('scene is not initialized yet')

    @Slot()
    def _handle_attention_project_changed(self):
        self.attention_scene_editable_changed.emit(self._scene_initializer_service.project() is not None)
