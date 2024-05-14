from PySide6.QtWidgets import QWidget, QToolBar, QLabel, QVBoxLayout, QApplication, QSizePolicy, QMainWindow, QWidgetAction, QFileDialog, QMessageBox

from .render_window import RenderWindow


class RenderWidget(QWidget):
    def __init__(self,
                 render_window:RenderWindow) -> None:
        super().__init__()

        vbox = QVBoxLayout()
        self.render_window = render_window
        self._view_widget = QWidget.createWindowContainer(self.render_window)
        self._view_widget.setMinimumSize(300, 300)
        self._view_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        vbox.addWidget(self._view_widget)
        self.setLayout(vbox)