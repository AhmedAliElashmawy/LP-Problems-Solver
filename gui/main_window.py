from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QApplication, 
                           QLineEdit, QComboBox, QLabel, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .styles import setup_styles
from .table_manager import TableManager
from .widgets_manager import WidgetsManager
from .solution_window import SolutionWindow
from .latex_renderer import LatexRenderer
from lp_solver import LPSolver

class MathLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Times New Roman", 12))
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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
        self.solution_window = SolutionWindow(self)
        
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
        # Collect problem type and method
        problem_type = "Minimization" if self.min_radio.isChecked() else "Maximization"
        
        # Get method and counts
        method = ""
        if self.simplex_radio.isChecked(): method = "Simplex"
        elif self.bigm_radio.isChecked(): method = "Big-M"
        elif self.twophase_radio.isChecked(): method = "Two-Phase"
        elif self.goal_programming.isChecked(): method = "Goal Programming"

        # Objective function coefficients
        obj_coeffs = []
        for col in range(self.obj_table.columnCount()):
            widget = self.obj_table.cellWidget(0, col)
            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
                obj_coeffs.append(text if text else "0")
            else:
                obj_coeffs.append("0")

        # Constraints
        constraints = []
        for row in range(self.constraint_table.rowCount()):
            row_data = []
            for col in range(self.constraint_table.columnCount()):
                widget = self.constraint_table.cellWidget(row, col)
                if isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    row_data.append(text if text else "0")
                elif isinstance(widget, QComboBox):
                    row_data.append(widget.currentText())
                else:
                    row_data.append("0")
            constraints.append(row_data)

        # Get variable names from table headers
        var_names = []
        for col in range(self.obj_table.columnCount()):
            header_item = self.obj_table.horizontalHeaderItem(col)
            var_names.append(header_item.text() if header_item else f"x{col+1}")

        # Format objective function terms for LaTeX
        obj_terms = []
        for i, c in enumerate(obj_coeffs):
            if c != "0":
                if c == "1":
                    obj_terms.append(f"x_{{{i+1}}}")
                elif c == "-1":
                    obj_terms.append(f"-x_{{{i+1}}}")
                else:
                    obj_terms.append(f"{c}x_{{{i+1}}}")

        # Format constraints for LaTeX
        latex_constraints = []
        # Extract constraint components
        constraint_coeffs = []
        rhs_values = []
        rel_operators = []
        restricted = []
        
        # Get restriction values from var_restrictions_table
        for col in range(self.obj_table.columnCount()):
            widget = self.var_restrictions_table.cellWidget(0, col)
            if widget is None:
                restricted.append(True)  # Default to restricted if widget is None
            elif widget.currentText() == "Unrestricted":
                restricted.append(False)
            else:
                restricted.append(True)

        for c in constraints:
            # Get coefficients excluding relation and RHS
            coeffs = c[:-2]
            constraint_coeffs.append([float(coef) for coef in coeffs])
            # Get relation operator
            rel_operators.append(c[-2])
            # Get RHS value
            rhs_values.append(float(c[-1]))
            
            # Continue with LaTeX formatting
            terms = []
            for i, coef in enumerate(coeffs):
                if coef != "0":
                    if coef == "1":
                        terms.append(f"x_{{{i+1}}}")
                    elif coef == "-1":
                        terms.append(f"-x_{{{i+1}}}")
                    else:
                        terms.append(f"{coef}x_{{{i+1}}}")
            
            operator = c[-2].replace("<=", r"\leq").replace(">=", r"\geq")
            constraint_str = f"{' + '.join(terms)} {operator} {c[-1]}"
            latex_constraints.append(constraint_str)

        # Convert objective coefficients to float
        obj_coeffs = [float(coef) for coef in obj_coeffs]

        # Create solution content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Render problem using LaTeX
        math_label = QLabel()
        math_pixmap = LatexRenderer.render_lp_problem(
            problem_type.lower(),
            obj_terms,
            latex_constraints
        )
        math_label.setPixmap(math_pixmap)
        math_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(math_label)

        # Debug prints
        print("Maximize flag:", not self.min_radio.isChecked())
        print("Objective coefficients:", obj_coeffs)
        print("Constraint coefficients matrix:", constraint_coeffs)
        print("RHS values:", rhs_values)
        print("Relation operators:", rel_operators)
        print("Restricted variables flags:", restricted)

        # Call solver with all parameters
        solver = LPSolver()
        # error, steps = solver.simplex(
        #     not self.min_radio.isChecked(),  # maximize flag
        #     obj_coeffs,                      # objective coefficients
        #     constraint_coeffs,               # constraint coefficients matrix
        #     rhs_values,                      # right-hand side values
        #     rel_operators,                   # relation operators
        #     restricted                       # restricted variables flags
        # )
        error, steps = solver.goal_programming_with_priority_values(
            not self.min_radio.isChecked(),  # maximize flag
            obj_coeffs,                      # objective coefficients
            constraint_coeffs,               # constraint coefficients matrix
            rhs_values,                      # right-hand side values
            rel_operators,                   # relation operators
            [1, 2, 3, 4]                    # priority values
        )

        # Convert DataFrame steps to string representation
        string_steps = []
        for step in steps:
            if hasattr(step, 'to_string'):  # Check if it's a DataFrame
                string_steps.append(step.to_string())
            else:
                string_steps.append(str(step))

        final_answer = "Final answer goes here"
        
        self.hide()
        self.solution_window.display_native_solution(content_widget, string_steps, final_answer)
        self.solution_window.show()
        self.solution_window.raise_()
        self.solution_window.activateWindow()
        
    def show_input_widgets(self):
        self.show()
        self.raise_()  # Bring window to front
        self.activateWindow()  # Activate the window
