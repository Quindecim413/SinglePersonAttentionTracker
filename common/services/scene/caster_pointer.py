from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QColor
from PySide6.QtCore import QUrl
from pathlib import Path


class CasterPointerEntity(Qt3DCore.QEntity):
    def __init__(self, color='yellow', parent=None) -> None:
        super().__init__(parent)
        self._pointer_mesh = Qt3DRender.QMesh()
        # self._pointer_mesh.statusChanged.connect(lambda status: print(f'{status=}, {self._pointer_mesh.status()=}'))
        self._pointer_mesh.setSource(QUrl.fromLocalFile(Path(__file__).parent / 'src3d/pointer.obj'))
        self._pointer_transform = Qt3DCore.QTransform()
        self._pointer_material = Qt3DExtras.QPhongMaterial()
        
        self.addComponent(self._pointer_mesh)
        self.addComponent(self._pointer_transform)
        self.addComponent(self._pointer_material)
        
        self._pointer_material.setAmbient(QColor(color))
