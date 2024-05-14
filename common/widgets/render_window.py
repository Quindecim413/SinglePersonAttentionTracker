from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QMouseEvent, QQuaternion, QScreen, QVector3D, QColor, QAction)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtCore import Signal, QPoint

class RenderWindow(Qt3DExtras.Qt3DWindow):
    mouse_double_clicked = Signal(QPoint)
    def __init__(self):
        super().__init__()
        self.renderSettings().pickingSettings().setPickMethod(Qt3DRender.QPickingSettings.PickMethod.TrianglePicking)
        self.renderSettings().pickingSettings().setPickResultMode(Qt3DRender.QPickingSettings.PickResultMode.NearestPick)
        self.renderSettings().pickingSettings().setWorldSpaceTolerance(0.001)
        print('world space tollerance:',self.renderSettings().pickingSettings().worldSpaceTolerance())
        # Camera
        self.camera().lens().setPerspectiveProjection(60, 16 / 9, 0.1, 1000)
        self.camera().setPosition(QVector3D(0, 0, 5))
        self.camera().setViewCenter(QVector3D(0, 0, -1))

        frustrum:Qt3DRender.QFrustumCulling = self.activeFrameGraph().findChild(Qt3DRender.QFrustumCulling) # type: ignore
        render_state = Qt3DRender.QRenderStateSet(frustrum)
        self._face_culling = Qt3DRender.QCullFace(render_state)
        self._face_culling.setMode(Qt3DRender.QCullFace.CullingMode.NoCulling)
        render_state.addRenderState(self._face_culling)
        some_node = frustrum.children()[0]
        some_node.setParent(None)
        some_node.deleteLater()

        # For camera controls
        self._rootEntity = Qt3DCore.QEntity()
        self.setRootEntity(self._rootEntity)
        
        self.camController = Qt3DExtras.QFirstPersonCameraController(self._rootEntity)
        
        self.camController.setLinearSpeed(1.5)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(self.camera())
        self.activeFrameGraph()


    def root_entity(self):
        return self._rootEntity
    
    def mouseDoubleClickEvent(self, ev: QMouseEvent) -> None:
        self.mouse_double_clicked.emit(ev.pos())
        return super().mouseDoubleClickEvent(ev)
