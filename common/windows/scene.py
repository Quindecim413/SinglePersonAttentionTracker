from PySide6.QtCore import Qt, Slot, QUrl, QSize
from PySide6.QtGui import QCloseEvent, QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QPushButton, QStackedWidget, QSizePolicy, QToolBar, QToolButton
from pathlib import Path

from common.services.scene.scene_3d import AttentionScene3DService



class SceneWindow(QMainWindow):
    # https://www.flaticon.com/free-icon/touchscreen_3601893?term=selectable&related_id=3601893
    def __init__(self, 
                 render_widget:QWidget,
                 scene_3d_service:AttentionScene3DService) -> None:
        super().__init__()
        self.render_widget = render_widget
        self.scene_3d_service = scene_3d_service
        
        self.scene_3d_service.elements_selectable_by_picking_changed.connect(self._observe_elements_selectable_by_picking_changed)

        w = QWidget()
        vbox = QVBoxLayout()
        w.setLayout(vbox)

        src_path = Path(__file__).parent / 'src'

        selectable_icon_path = str((src_path / 'selectable.png').resolve())
        not_selectable_icon_path = str((src_path / 'not-selectable.png').resolve())

        icon = QIcon()
        
        icon.addFile(not_selectable_icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.On)
        icon.addFile(selectable_icon_path, QSize(), QIcon.Mode.Active, QIcon.State.Off)
        
        self.toolbar = QToolBar("")
        self.addToolBar(self.toolbar)

        self.elements_selectable_action = QAction(icon, 'Выбирать кликом')
        self.elements_selectable_action.setToolTip('Отлючает/включает возможность выбора элемента сцены нажатием')
        self.elements_selectable_action.setCheckable(True)

        self.elements_selectable_action.toggled.connect(self._handle_elements_selectable_button_toggled)
        self.elements_selectable_action.setChecked(not self.scene_3d_service.elements_selectable_by_picking())

        self.toolbar.addAction(self.elements_selectable_action)

        vbox.addWidget(self.render_widget)
        

        self.setCentralWidget(w)

    @Slot(bool)
    def _observe_elements_selectable_by_picking_changed(self, is_selectable:bool):
        self.elements_selectable_action.setChecked(not is_selectable)

    @Slot(bool)
    def _handle_elements_selectable_button_toggled(self, is_pressed:bool):
        self.scene_3d_service.set_elements_selectable_by_picking(not is_pressed)

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        self.hide()

    def bring_to_front(self):
        if self.isMinimized():
            self.showNormal()  # Restores the window if it was minimized.
        if self.isHidden():
            self.show()
        self.raise_()        # Brings the window to the front.
        self.activateWindow()  # Gives the window focus.

