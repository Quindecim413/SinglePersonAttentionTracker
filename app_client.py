import sys

from PySide6.QtWidgets import  QApplication
from client_app.container import ClientAppContainer

import logging
# Configure logging
logging.basicConfig(
    # filename='app.log', 
    level=logging.DEBUG,
    format='%(levelname)s:%(filename)s:%(lineno)d:%(message)s')

container = ClientAppContainer()

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

sys._excepthook = sys.excepthook  # Backup the original excepthook #type:ignore
sys.excepthook = exception_hook  # Set the custom excepthook

main_window = None
def show_main_window():
    global main_window
    
    main_window = container.app_view()
    main_window.show()
      
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)

        QTimer.singleShot(0, show_main_window)
        sys.exit(app.exec())
    except Exception as e:
        logging.exception("An error occurred: %s", e)
        print(f"An error occurred: {e}")
        app.quit()
