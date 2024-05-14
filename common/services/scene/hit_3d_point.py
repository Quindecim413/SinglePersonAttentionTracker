from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QColor


class Hit3DPoint(Qt3DCore.QEntity):
    def __init__(self, color:QColor|None=None, parent=None) -> None:
        super().__init__(parent)
        self.material = Qt3DExtras.QPhongMaterial(self)
        self.material.setAmbient(QColor('yellow'))# if color is None else color)
        
        self.sphereMesh = Qt3DRender.QMesh()
        self.sphereMesh.setSource(QUrl.fromLocalFile(Path(__file__).parent/'src3d/attention_point.obj'))
        # self.sphereMesh.statusChanged.connect(lambda status: print(f'{status=}, {self.sphereMesh.status()=}'))
        self.sphereTransform = Qt3DCore.QTransform()
        
        self.addComponent(self.sphereTransform)
        self.addComponent(self.material)
        self.addComponent(self.sphereMesh)

    def set_color(self, color):
        self.material.setAmbient(color)
    
    def transform(self):
        return self.sphereTransform
    
    def hide(self):
        if self.isEnabled():
            self.setEnabled(False)
    
    def reveal(self):
        if not self.isEnabled():
            self.setEnabled(True)