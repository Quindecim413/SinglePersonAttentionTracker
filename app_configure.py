import sys

from PySide6.QtWidgets import  QApplication
import logging
from configurator_app.container import ConfiguratorAppContainer
# Configure logging
logging.basicConfig(
    # filename='app.log', 
    level=logging.DEBUG,
    format='%(levelname)s:%(filename)s:%(lineno)d:%(message)s')


from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer
import traceback

# Override the excepthook
def exception_hook(exc_type, exc_value, exc_traceback):
    print(f"Uncaught exception:", exc_value, file=sys.stderr)
    print(traceback.format_exc())
    
    QTimer.singleShot(0, app.quit)
    sys._excepthook(exc_type, exc_value, exc_traceback)  # Call the original excepthook #type:ignore
    raise exc_value


sys._excepthook = sys.excepthook  # Backup the original excepthook # type: ignore 
sys.excepthook = exception_hook  # Set the custom excepthook


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    
    container = ConfiguratorAppContainer()
    widg = container.configure_window()
    widg.show()
    sys.exit(app.exec())