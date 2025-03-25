import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import LPSolverGUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_icon = QIcon("contour.png")
    app.setWindowIcon(app_icon)
    window = LPSolverGUI() 
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())


