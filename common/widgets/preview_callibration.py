from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel

from common.dtos.calibration import CallibrationRecord



class CallibrationRecordPreviewWidget(QWidget):
    def __init__(self, record:CallibrationRecord) -> None:
        super().__init__()
        self._record = record
        point_position = self._record.callibration_point_position
        head_position = self._record.head_props.position
        head_rotation = self._record.head_props.rotation.toEulerAngles()


        grid_position = QGridLayout()
        grid_position.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)
        grid_position.addWidget(QLabel('x'), 0, 0); grid_position.addWidget(QLabel(str(round(point_position.x(), 2))), 0, 1)
        grid_position.addWidget(QLabel('y'), 1, 0); grid_position.addWidget(QLabel(str(round(point_position.y(), 2))), 1, 1)
        grid_position.addWidget(QLabel('z'), 2, 0); grid_position.addWidget(QLabel(str(round(point_position.z(), 2))), 2, 1)

        
        grid_head_position = QGridLayout()
        grid_head_position.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)
        grid_head_position.addWidget(QLabel('x'), 0, 0); grid_head_position.addWidget(QLabel(str(round(head_position.x(), 2))), 0, 1)
        grid_head_position.addWidget(QLabel('y'), 1, 0); grid_head_position.addWidget(QLabel(str(round(head_position.y(), 2))), 1, 1)
        grid_head_position.addWidget(QLabel('z'), 2, 0); grid_head_position.addWidget(QLabel(str(round(head_position.z(), 2))), 2, 1)

        grid_head_rotation = QGridLayout()
        grid_head_rotation.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)
        grid_head_rotation.addWidget(QLabel('yaw'), 0, 0);   grid_head_rotation.addWidget(QLabel(str(round(head_rotation.z(), 2))), 0, 1)
        grid_head_rotation.addWidget(QLabel('pitch'), 1, 0); grid_head_rotation.addWidget(QLabel(str(round(head_rotation.x(), 2))), 1, 1)
        grid_head_rotation.addWidget(QLabel('roll'), 2, 0);  grid_head_rotation.addWidget(QLabel(str(round(head_rotation.y(), 2))), 2, 1)


        grid = QGridLayout()

        grid.addWidget(QLabel('Координаты точка калибровки'), 0, 0)
        grid.addWidget(QLabel('Положение головы'), 0, 1)
        grid.addWidget(QLabel('Вращение головы'), 0, 1)

        grid.addLayout(grid_position, 1, 0)
        grid.addLayout(grid_head_position, 1, 1)
        grid.addLayout(grid_head_rotation, 1, 2)


        self.setLayout(grid)

        
        

