import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import LPSolverGUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LPSolverGUI()
    window.show()
    sys.exit(app.exec())
