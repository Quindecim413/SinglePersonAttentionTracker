from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DCore import Qt3DCore
from PySide6.QtCore import Signal, Property,  QPropertyAnimation, Slot
from PySide6.QtGui import QVector3D, QMatrix4x4
from attr import dataclass
import numpy as np

class ForwardRaysCaster(Qt3DRender.QRayCaster):
    hit_detected = Signal(Qt3DRender.QRayCasterHit)
    hit_missed = Signal()
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setRunMode(Qt3DRender.QRayCaster.RunMode.Continuous)
        self.hitsChanged.connect(self._process_hits)
        self.setShareable(False)
        self.setLength(50)
        self.setDirection(QVector3D(0,0,-1))

    def _process_hits(self):
        hits = self.hits()
        if len(hits) > 0:
            if len(hits) > 1:
                closest_hit = min(*hits, key=lambda hit: hit.distance())
            else:
                closest_hit = hits[0]
            self.hit_detected.emit(closest_hit)


class SingleRaysCasterPlaceHolder(Qt3DCore.QEntity):
    hit_detected = Signal(Qt3DRender.QRayCasterHit)
    hit_missed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._ray_caster = Qt3DRender.QRayCaster(self)
        self._ray_caster.setShareable(False)
        self._transform = Qt3DCore.QTransform()
        
        self.addComponent(self._ray_caster)
        self.addComponent(self._transform)

        self._ray_caster.setRunMode(Qt3DRender.QRayCaster.RunMode.Continuous)
        self._ray_caster.setLength(50)
        self._ray_caster.setDirection(QVector3D(0,0,-1))
        self._ray_caster.hitsChanged.connect(self._process_hits)
        self._ray_caster.setEnabled(True)

        self.setEnabled(False)

    def ray_caster(self):
        return self._ray_caster
    
    # def set_casting(self, is_casting:bool):
    #     self._ray_caster.setEnabled(bool(is_casting))
    #     if is_casting:
    #         self._ray_caster.trigger()

    def transform(self):
        return self._transform
    
    def _process_hits(self):
        hits = self._ray_caster.hits()
        
        if len(hits) > 0:
            if len(hits) > 1:
                closest_hit = min(*hits, key=lambda hit: hit.distance())
            else:
                closest_hit = hits[0]
            self.hit_detected.emit(closest_hit)
        else:
            self.hit_missed.emit()

@dataclass
class CastResult:
    is_succesfull:bool
    hit:Qt3DRender.QRayCasterHit|None

@dataclass
class AggregatedCastResult:
    casts:list[CastResult]

class MultipleRayCastersEntity(Qt3DCore.QEntity):
    cast_results_aggregated = Signal(AggregatedCastResult)
    is_casting_rays_changed = Signal(bool)

    def __init__(self, num=10, angle=10, parent = None) -> None:
        super().__init__(parent)
        self.transform = Qt3DCore.QTransform(self)
        self.addComponent(self.transform)
        self._matrix = QMatrix4x4()
        self._rotation_angle = 0
        self.sphereRotateTransformAnimation = QPropertyAnimation(self, b'rotationAngle', self)
        self.sphereRotateTransformAnimation.setStartValue(0)
        self.sphereRotateTransformAnimation.setEndValue(360)
        self.sphereRotateTransformAnimation.setDuration(1000)
        self.sphereRotateTransformAnimation.setLoopCount(-1)
        self.sphereRotateTransformAnimation.start()

        angles = np.linspace(-angle*1.0, angle*1.0, num=num, endpoint=False)

        self._single_ray_placeholders: list[SingleRaysCasterPlaceHolder] = []

        self._caster2ind:dict[SingleRaysCasterPlaceHolder, int] = dict()

        self._caster2cast_results_at_one_frame: dict[SingleRaysCasterPlaceHolder, CastResult] = dict()

        for angle in angles:
            matrix = QMatrix4x4()
            matrix.rotate(angle, QVector3D(1, 0, 0))
            matrix.rotate(360/2/num, QVector3D(0, 0, -1))
            single_ray_placeholder = SingleRaysCasterPlaceHolder(self)
            single_ray_placeholder.transform().setMatrix(matrix)
            self._single_ray_placeholders.append(single_ray_placeholder)
            single_ray_placeholder.hit_detected.connect(self._hit_detected)
            single_ray_placeholder.hit_missed.connect(self._hit_missed)
        
        self._is_casting_rays = False
    
    @Slot(Qt3DRender.QRayCasterHit)
    def _hit_detected(self, hit:Qt3DRender.QRayCasterHit):
        if isinstance(caster_placeholder:=self.sender(), SingleRaysCasterPlaceHolder):
            if caster_placeholder not in self._caster2cast_results_at_one_frame:
                self._caster2cast_results_at_one_frame[caster_placeholder] = CastResult(True, hit)
                self._process_hits_at_one_frame_aggregation()
    @Slot()
    def _hit_missed(self):
        if isinstance(caster_placeholder:=self.sender(), SingleRaysCasterPlaceHolder):
            if caster_placeholder not in self._caster2cast_results_at_one_frame:
                self._caster2cast_results_at_one_frame[caster_placeholder] = CastResult(False, None)
                self._process_hits_at_one_frame_aggregation()

    def _process_hits_at_one_frame_aggregation(self):
        if len(self._caster2cast_results_at_one_frame) == len(self._single_ray_placeholders):
            aggregated_cast_results = AggregatedCastResult(casts=list(self._caster2cast_results_at_one_frame.values()))
            self._caster2cast_results_at_one_frame.clear()
            self.cast_results_aggregated.emit(aggregated_cast_results)

    def casters(self):
        return list(self._single_ray_placeholders)

    def setRotationAngle(self, angle):
        self._rotation_angle = angle
        self._matrix.setToIdentity()
        self._matrix.rotate(angle, QVector3D(0, 0, -1))
        self.transform.setMatrix(self._matrix)

    def getRotationAngle(self):
        return self._rotation_angle
    
    rotationAngle = Property(float, getRotationAngle, setRotationAngle)
    
    def addLayer(self, layer: Qt3DRender.QLayer):
        for placeholder in self._single_ray_placeholders:
            placeholder.ray_caster().addLayer(layer)

    def is_casting_rays(self):
        return self._is_casting_rays

    def set_casting_rays(self, casting=True):
        casting = bool(casting)
        if casting != self._is_casting_rays:
            for placeholder in self._single_ray_placeholders:
                placeholder.setEnabled(casting)
        self._is_casting_rays = casting
        self.is_casting_rays_changed.emit(casting)
