from pathlib import Path
from dependency_injector import providers, containers
from common.services.scene.repo import AttentionProjectsRepo
from PySide6.QtWidgets import QWidget
from common.windows.scene import SceneWindow
from .domain.interfaces import AttentionScene
from .services.scene.scene_3d import AttentionScene3DService
from .services.scene.initializer import AttentionSceneInitializerService
from .services.video.camera import CameraService
from .widgets.camera_configure import CameraConfigureVM, CameraConfigureWidget
from .widgets.render_widget import RenderWidget

from .widgets.render_window import RenderWindow
from .widgets.video_preview import VideoPreviewWidget


class SceneContainer(containers.DeclarativeContainer):
    
    render_window = providers.Singleton(RenderWindow)
    render_widget = providers.Singleton(RenderWidget, render_window=render_window)
    

    storage_dir = providers.Dependency(instance_of=Path)

    scene_3d_service = providers.Singleton(AttentionScene3DService, render_window=render_window)
    repo = providers.Singleton(AttentionProjectsRepo,
                               storage_dir=storage_dir)
    
    render_main_window = providers.Singleton(SceneWindow,
                                             render_widget=render_widget,
                                             scene_3d_service=scene_3d_service)
    
    initializer = providers.Singleton(AttentionSceneInitializerService, 
                                      attention_scene_3d_service=scene_3d_service,
                                      scene_repo=repo)

    # current:providers.Factory[IAttentionScene] = providers.Factory(initializer.provided.attention_scene.call())


class CameraSourceContainer(containers.DeclarativeContainer):
    camera_service = providers.Singleton(CameraService)
    camera_configure_vm = providers.Factory(CameraConfigureVM,
                                            camera_service=camera_service)
    empty_widget = providers.Factory(QWidget)
    camera_preview_widget = providers.Factory(VideoPreviewWidget,
                                             video_service=camera_service)

    camera_configure_widget = providers.Factory(CameraConfigureWidget,
                                                vm=camera_configure_vm,
                                                camera_preview_widget=camera_preview_widget
                                                )
    
# class ActivePersonContainer(containers.DeclarativeContainer):
#     scene = providers.DependenciesContainer()
#     person = providers.Factory(ActivePersonService,
#                                       scene_initializer=scene.initializer,
#                                       scene_3d=scene.scene_3d_service)