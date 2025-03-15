import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
                           QTableWidgetItem, QComboBox, QRadioButton, QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

class LPSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linear Programming Solver")
        self.resize(450, 350)
        
        # Initialize all instance variables first
        self.var_restrictions_table = QTableWidget()
        self.var_restrictions_label = QLabel("Variable Restrictions:")
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Apply styles
        self.setup_styles()
        self.center_window()
        
        # Create initial widgets (visible from start)
        self.create_initial_widgets()
        
        # Create rest of widgets (hidden initially)
        self.create_hidden_widgets()
        
        # Hide all widgets that should be initially invisible
        self.hide_widgets()

    def center_window(self):
        """Centers the window on the screen"""
        screen = QApplication.primaryScreen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def setup_styles(self):
        # Set application style
       self.setStyleSheet("""
    QMainWindow {
        background: #0F0F0F;
    }
    QGroupBox {
        font-weight: bold;
        border: 2px solid #2A2A2A;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 10px;
        background-color: #1C1C1C;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 2px 6px;
        color: #D0D0D0;
        background-color: transparent;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007ACC, stop:1 #005A9E);
        color: white;
        border: 1px solid #004C8C;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        transition: all 0.3s;
    }
    QPushButton:hover {
        background: #008CFF;
        border: 1px solid #006BB3;
    }
    QPushButton:pressed {
        background: #005A9E;
    }
    QHeaderView::section {
        background: #252526;
        padding: 6px;
        border: 1px solid #3A3A3A;
        font-weight: bold;
        color: #E0E0E0;
    }
    QLineEdit {
        border: 1px solid #333;
        border-radius: 6px;
        background-color: #1A1A1A;
        color: #E0E0E0;
        selection-background-color: #008CFF;
    }
    QLineEdit:focus {
        border: 2px solid #007ACC;
        background: #222;
    }
    QRadioButton {
        spacing: 8px;
        color: #E0E0E0;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid #007ACC;
    }
    QRadioButton::indicator::checked {
        background-color: #007ACC;
        border: 2px solid #005A9E;
    }
    QLabel {
        color: #D0D0D0;
        font-weight: bold;
    }
""")



    def create_initial_widgets(self):
        # Variable Restrictions
        var_restrictions_group = QGroupBox("Variable Restrictions")
        var_restrictions_layout = QHBoxLayout()
        self.non_negative_radio = QRadioButton("All Non-negative")
        self.unrestricted_radio = QRadioButton("Unrestricted")
        self.non_negative_radio.setChecked(True)
        self.unrestricted_radio.toggled.connect(self.on_restriction_change)
        var_restrictions_layout.addWidget(self.non_negative_radio)
        var_restrictions_layout.addWidget(self.unrestricted_radio)
        var_restrictions_group.setLayout(var_restrictions_layout)
        self.layout.addWidget(var_restrictions_group)
        
        # Add some spacing to group box layouts
        var_restrictions_layout.setSpacing(15)
        
        # Problem Size Inputs
        size_group = QGroupBox("Problem Size")
        size_layout = QHBoxLayout()
        self.var_count = QLineEdit()
        self.constraint_count = QLineEdit()
        self.var_count.setPlaceholderText("Variables")
        self.constraint_count.setPlaceholderText("Constraints")
        size_layout.addWidget(QLabel("Number of Variables:"))
        size_layout.addWidget(self.var_count)
        size_layout.addWidget(QLabel("Number of Constraints:"))
        size_layout.addWidget(self.constraint_count)
        size_group.setLayout(size_layout)
        self.layout.addWidget(size_group)
        
        # Add some spacing to group box layouts
        size_layout.setSpacing(15)
        
        # Solution Method
        self.method_group = QGroupBox("Solution Method")
        method_layout = QHBoxLayout()
        self.simplex_radio = QRadioButton("Simplex")
        self.bigm_radio = QRadioButton("Big-M")
        self.twophase_radio = QRadioButton("Two-Phase")
        self.goal_programming = QRadioButton("Goal Programming")
        self.simplex_radio.setChecked(True)
        for radio in [self.simplex_radio, self.bigm_radio, self.twophase_radio, self.goal_programming]:
            method_layout.addWidget(radio)
        self.method_group.setLayout(method_layout)
        self.layout.addWidget(self.method_group)
        
        # Add some spacing to group box layouts
        method_layout.setSpacing(15)

        # Create tables button
        self.create_tables_btn = QPushButton("Create Tables")
        self.create_tables_btn.clicked.connect(self.on_create_tables)
        self.layout.addWidget(self.create_tables_btn)

    def create_hidden_widgets(self):
        # Objective function table
        obj_layout = QVBoxLayout()
        obj_top_layout = QHBoxLayout()
        self.min_radio = QRadioButton("Minimize?")
        self.min_radio.setChecked(True)
        self.obj_label = QLabel("Objective Function:")
        obj_top_layout.addWidget(self.obj_label)
        obj_top_layout.addWidget(self.min_radio)
        obj_top_layout.addStretch()
        obj_layout.addLayout(obj_top_layout)
        
        self.obj_table = QTableWidget()
        self.obj_table.setFixedSize(800, 68)
        obj_layout.addWidget(self.obj_table)
        self.layout.addLayout(obj_layout)
        
        # Add spacing to layouts
        obj_layout.setSpacing(10)
        
        # Constraints table
        self.constraint_label = QLabel("Constraint Coefficients:")
        constraints_layout = QVBoxLayout()
        self.constraint_table = QTableWidget()
        constraints_layout.addWidget(self.constraint_label)
        constraints_layout.addWidget(self.constraint_table)
        self.layout.addLayout(constraints_layout)
        
        # Add spacing to layouts
        constraints_layout.setSpacing(10)

        # Add variable restrictions section
        var_rest_layout = QVBoxLayout()
        var_rest_layout.addWidget(self.var_restrictions_label)
        var_rest_layout.addWidget(self.var_restrictions_table)
        self.var_restrictions_table.setFixedSize(800, 68)  # Match obj_table size
        self.layout.addLayout(var_rest_layout)
        
        # Add spacing to layouts
        var_rest_layout.setSpacing(10)
        
        # Solve and Clear buttons
        button_layout = QHBoxLayout()
        self.solve_btn = QPushButton("Solve")
        self.clear_btn = QPushButton("Clear")
        button_layout.addWidget(self.solve_btn)
        button_layout.addWidget(self.clear_btn)
        self.layout.addLayout(button_layout)
        
        # Add spacing to layouts
        button_layout.setSpacing(15)
        
        # Connect buttons
        self.clear_btn.clicked.connect(self.clear_all)
        self.solve_btn.clicked.connect(self.solve_problem)

    def hide_widgets(self):
        # Hide all widgets that should be initially invisible
        widgets_to_hide = [
            self.obj_table,
            self.obj_label,
            self.min_radio,
            self.obj_table,
            self.constraint_label,
            self.constraint_table,
            self.solve_btn,
            self.clear_btn,
            self.var_restrictions_table,
            self.var_restrictions_label
        ]
        for widget in widgets_to_hide:
            widget.hide()

    def on_create_tables(self):
        # Replace setGeometry with resize and center
        self.resize(800, 600)
        self.center_window()
        # First create the tables
        self.create_tables()
        
        # Disable Problem Size inputs
        self.var_count.setEnabled(False)
        self.constraint_count.setEnabled(False)
        
        # Disable Variable Restrictions radio buttons
        self.non_negative_radio.setEnabled(False)
        self.unrestricted_radio.setEnabled(False)
        
        # Then show all hidden widgets
        widgets_to_show = [
            self.min_radio,
            self.obj_table,
            self.obj_label,
            self.constraint_label,
            self.constraint_table,
            self.method_group,
            self.solve_btn,
            self.clear_btn
        ]
        for widget in widgets_to_show:
            widget.show()

        self.create_tables_btn.hide()

    def create_tables(self):
        try:
            vars_count = int(self.var_count.text())
            constraints_count = int(self.constraint_count.text())

            # Set up objective function table
            self.obj_table.setRowCount(1)
            self.obj_table.setColumnCount(vars_count)

            obj_header_item = QTableWidgetItem("z")
            self.obj_table.setVerticalHeaderItem(0, obj_header_item)

            # Set up constraints table
            self.constraint_table.setRowCount(constraints_count)
            self.constraint_table.setColumnCount(vars_count + 2)

            # Add headers for variables (editable)
            for i in range(vars_count):
                var_name = f"x{i+1}"
                obj_header = QTableWidgetItem(var_name)
                constraint_header = QTableWidgetItem(var_name)

                self.obj_table.setHorizontalHeaderItem(i, obj_header)
                self.constraint_table.setHorizontalHeaderItem(i, constraint_header)

            # Set headers for Relation & RHS (not editable)
            relation_header = QTableWidgetItem("Relation")
            relation_header.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Disable editing

            rhs_header = QTableWidgetItem("RHS")
            rhs_header.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Disable editing

            self.constraint_table.setHorizontalHeaderItem(vars_count, relation_header)
            self.constraint_table.setHorizontalHeaderItem(vars_count + 1, rhs_header)

            # Add relation comboboxes
            for i in range(constraints_count):
                relation_combo = QComboBox()
                relation_combo.addItems(["<=", "=", ">="])
                self.constraint_table.setCellWidget(i, vars_count, relation_combo)

            # Enable header editing with sync
            self.obj_table.horizontalHeader().sectionDoubleClicked.connect(lambda index: self.edit_header(index, vars_count))

            # Update variable restrictions table if unrestricted is selected
            if self.unrestricted_radio.isChecked():
                self.setup_var_restrictions_table(vars_count)
                self.var_restrictions_table.show()
                self.var_restrictions_label.show()

        except ValueError:
            pass

    def edit_header(self, index, vars_count):
        """ Allows user to edit variable names and sync changes to both tables """
        old_text = self.obj_table.horizontalHeaderItem(index).text()
        
        line_edit = QLineEdit(old_text, self.obj_table)
        line_edit.setFrame(False)
        line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_edit.setGeometry(self.obj_table.horizontalHeader().sectionPosition(index) + 28, 0,
                            self.obj_table.horizontalHeader().sectionSize(index), self.obj_table.horizontalHeader().height())

        line_edit.editingFinished.connect(lambda: self.update_header(index, line_edit, vars_count))
        line_edit.setFocus()
        line_edit.show()

    def update_header(self, index, line_edit, vars_count):
        """ Updates headers in both tables """
        new_text = line_edit.text().strip()
        if new_text:
            # Update headers in all tables
            self.obj_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
            self.constraint_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
            if self.unrestricted_radio.isChecked():
                self.var_restrictions_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
        line_edit.deleteLater()

    def on_restriction_change(self, checked):
        if checked:
            try:
                vars_count = int(self.var_count.text())
                self.setup_var_restrictions_table(vars_count)
                self.var_restrictions_table.show()
                self.var_restrictions_label.show()
            except ValueError:
                pass
        else:
            self.var_restrictions_table.hide()
            self.var_restrictions_label.hide()

    def setup_var_restrictions_table(self, vars_count):
        self.var_restrictions_table.setRowCount(1)
        self.var_restrictions_table.setColumnCount(vars_count)
        self.var_restrictions_table.setFixedSize(800, 68)  # Match obj_table size
        
        # Set headers and sync with existing table headers
        for i in range(vars_count):
            var_name = self.obj_table.horizontalHeaderItem(i).text() if self.obj_table.horizontalHeaderItem(i) else f"x{i+1}"
            header = QTableWidgetItem(var_name)
            self.var_restrictions_table.setHorizontalHeaderItem(i, header)
            
            # Add combobox for each variable
            combo = QComboBox()
            combo.addItems(["Unrestricted", "≥ 0", "≤ 0"])
            self.var_restrictions_table.setCellWidget(0, i, combo)

    def clear_all(self):
        self.var_count.clear()
        self.constraint_count.clear()
        self.obj_table.setRowCount(0)
        self.constraint_table.setRowCount(0)
        self.min_radio.setChecked(True)
        self.simplex_radio.setChecked(True)
        self.hide_widgets()
        self.create_tables_btn.show()
        self.var_count.setEnabled(True)
        self.constraint_count.setEnabled(True)
        self.non_negative_radio.setEnabled(True)
        self.unrestricted_radio.setEnabled(True)
        self.var_restrictions_table.setRowCount(0)
        self.var_restrictions_table.hide()
        self.var_restrictions_label.hide()
        self.resize(450, 350)
        self.center_window()

    def solve_problem(self):
        # To be implemented
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LPSolverGUI()
    window.show()
    sys.exit(app.exec())
