from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from .styles import setup_styles
from .table_manager import TableManager
from .widgets_manager import WidgetsManager

class LPSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linear Programming Solver")
        self.resize(450, 350)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Initialize managers
        self.table_manager = TableManager(self)
        self.widgets_manager = WidgetsManager(self)
        
        # Apply styles and setup window
        setup_styles(self)
        self.center_window()
        
        # Create widgets
        self.widgets_manager.create_initial_widgets()
        self.widgets_manager.create_hidden_widgets()
        self.widgets_manager.hide_widgets()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def solve_problem(self):
        # To be implemented with solver logic
        pass
