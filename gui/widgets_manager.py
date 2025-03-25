from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class WidgetsManager:
    def __init__(self, parent):
        self.parent = parent
        self.initialize_widgets()

    def initialize_widgets(self):
        self.parent.var_restrictions_table = QTableWidget()
        self.parent.var_restrictions_label = QLabel("Variable Restrictions:")
        self.parent.priority_table = QTableWidget()
        self.parent.priority_label = QLabel("Priority Levels:")
        self.parent.obj_table = QTableWidget()
        self.parent.constraint_table = QTableWidget()

    def create_initial_widgets(self):
        # Variable Restrictions
        var_restrictions_group = QGroupBox("Variable Restrictions")
        var_restrictions_layout = QHBoxLayout()
        self.parent.non_negative_radio = QRadioButton("All Non-negative")
        self.parent.unrestricted_radio = QRadioButton("Unrestricted")
        self.parent.non_negative_radio.setChecked(True)
        var_restrictions_layout.addWidget(self.parent.non_negative_radio)
        var_restrictions_layout.addWidget(self.parent.unrestricted_radio)
        var_restrictions_group.setLayout(var_restrictions_layout)
        self.parent.layout.addWidget(var_restrictions_group)

        # Problem Size
        size_group = QGroupBox("Problem Size")
        size_layout = QHBoxLayout()
        self.parent.var_count = QLineEdit()
        self.parent.constraint_count = QLineEdit()
        self.parent.var_count.setPlaceholderText("Variables")
        self.parent.constraint_count.setPlaceholderText("Constraints")
        size_layout.addWidget(QLabel("Number of Variables:"))
        size_layout.addWidget(self.parent.var_count)
        size_layout.addWidget(QLabel("Number of Constraints:"))
        size_layout.addWidget(self.parent.constraint_count)
        size_group.setLayout(size_layout)
        self.parent.layout.addWidget(size_group)

        # Solution Method
        method_group = QGroupBox("Solution Method")
        method_layout = QHBoxLayout()
        self.parent.simplex_radio = QRadioButton("Simplex")
        self.parent.bigm_radio = QRadioButton("Big-M")
        self.parent.twophase_radio = QRadioButton("Two-Phase")
        self.parent.goal_programming = QRadioButton("Goal Programming")
        self.parent.simplex_radio.setChecked(True)
        for radio in [self.parent.simplex_radio, self.parent.bigm_radio, 
                     self.parent.twophase_radio, self.parent.goal_programming]:
            method_layout.addWidget(radio)
        method_group.setLayout(method_layout)
        self.parent.layout.addWidget(method_group)

        # Create tables button
        self.parent.create_tables_btn = QPushButton("Create Tables")
        self.parent.create_tables_btn.clicked.connect(self.on_create_tables)
        self.parent.layout.addWidget(self.parent.create_tables_btn)
        

    def create_hidden_widgets(self):
        # Objective function
        obj_layout = QVBoxLayout()
        obj_top_layout = QHBoxLayout()
        self.parent.min_radio = QRadioButton("Minimize?")
        self.parent.min_radio.setChecked(True)
        self.parent.obj_label = QLabel("Objective Function:")
        obj_top_layout.addWidget(self.parent.obj_label)
        obj_top_layout.addWidget(self.parent.min_radio)
        obj_top_layout.addStretch()
        obj_layout.addLayout(obj_top_layout)
        obj_layout.addWidget(self.parent.obj_table)
        self.parent.layout.addLayout(obj_layout)

        # Add other widgets and layouts
        self.parent.constraint_label = QLabel("Constraint Coefficients:")
        self.parent.layout.addWidget(self.parent.constraint_label)
        self.parent.layout.addWidget(self.parent.constraint_table)
        
        # Add variable restrictions (but keep hidden by default)
        self.parent.layout.addWidget(self.parent.var_restrictions_label)
        self.parent.layout.addWidget(self.parent.var_restrictions_table)
        self.parent.var_restrictions_label.hide()
        self.parent.var_restrictions_table.hide()

        # Add priority table with radio button (but keep hidden by default)
        priority_top_layout = QHBoxLayout()
        self.parent.priority_label = QLabel("Priority:")
        self.parent.priority_radio = QRadioButton("Level?")
        self.parent.priority_radio.setChecked(True)
        priority_top_layout.addWidget(self.parent.priority_label)
        priority_top_layout.addWidget(self.parent.priority_radio)
        priority_top_layout.addStretch()
        self.parent.layout.addLayout(priority_top_layout)
        self.parent.layout.addWidget(self.parent.priority_table)
        self.parent.priority_label.hide()
        self.parent.priority_radio.hide()
        self.parent.priority_table.hide()

        # Buttons
        button_layout = QHBoxLayout()
        self.parent.solve_btn = QPushButton("Solve")
        self.parent.clear_btn = QPushButton("Clear")
        button_layout.addWidget(self.parent.solve_btn)
        button_layout.addWidget(self.parent.clear_btn)
        self.parent.layout.addLayout(button_layout)
        
        # Connect buttons
        self.parent.clear_btn.clicked.connect(self.clear_all)
        self.parent.solve_btn.clicked.connect(self.parent.solve_problem)

    def hide_widgets(self):
        widgets = [
            self.parent.obj_table, self.parent.obj_label, self.parent.min_radio,
            self.parent.constraint_label, self.parent.constraint_table,
            self.parent.solve_btn, self.parent.clear_btn,
            self.parent.var_restrictions_table, self.parent.var_restrictions_label,
            self.parent.priority_table, self.parent.priority_label,
            self.parent.priority_radio
        ]
        for widget in widgets:
            widget.hide()

    def on_create_tables(self):
        self.parent.resize(800, 800)
        self.parent.center_window()
        self.parent.table_manager.create_tables()
        
        # Disable inputs and set color
        disabled_style = """QRadioButton::indicator::checked {
        background-color: #0d0d0d;
        border: 2px solid #050505;
        }
            QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid #050505;
    }"""
        self.parent.var_count.setEnabled(False)
        self.parent.constraint_count.setEnabled(False)
        
        radio_buttons = [
            self.parent.non_negative_radio,
            self.parent.unrestricted_radio,
            self.parent.simplex_radio,
            self.parent.bigm_radio,
            self.parent.twophase_radio,
            self.parent.goal_programming
        ]
        
        for radio in radio_buttons:
            radio.setEnabled(False)
            radio.setStyleSheet(disabled_style)
        
        # Show widgets
        widgets = [
            self.parent.min_radio, self.parent.obj_table, self.parent.obj_label,
            self.parent.constraint_label, self.parent.constraint_table,
            self.parent.solve_btn, self.parent.clear_btn
        ]
        for widget in widgets:
            if(self.parent.goal_programming.isChecked() and (widget == self.parent.min_radio or widget == self.parent.obj_table or widget == self.parent.obj_label)):
                continue
            widget.show()
        self.parent.create_tables_btn.hide()
        
        if self.parent.unrestricted_radio.isChecked():
            try:
                vars_count = int(self.parent.var_count.text())
                self.parent.table_manager.setup_var_restrictions_table(vars_count)
                self.parent.var_restrictions_table.show()
                self.parent.var_restrictions_label.show()
            except ValueError:
                pass
        
        if self.parent.goal_programming.isChecked():
            try:
                constraints_count = int(self.parent.constraint_count.text())
                self.parent.table_manager.setup_priority_table(constraints_count)
                self.parent.priority_table.show()
                self.parent.priority_label.show()
                self.parent.priority_radio.show()
            except ValueError:
                pass
        self.update_window_size()

    def clear_all(self):
        # Clear and reset all widgets
        self.parent.var_count.clear()
        self.parent.constraint_count.clear()
        self.parent.obj_table.setRowCount(0)
        self.parent.constraint_table.setRowCount(0)
        self.parent.min_radio.setChecked(True)
        self.parent.simplex_radio.setChecked(True)
        self.hide_widgets()
        self.parent.create_tables_btn.show()
        
        # Enable inputs
        self.parent.var_count.setEnabled(True)
        self.parent.constraint_count.setEnabled(True)
        radio_buttons = [
            self.parent.non_negative_radio,
            self.parent.unrestricted_radio,
            self.parent.simplex_radio,
            self.parent.bigm_radio,
            self.parent.twophase_radio,
            self.parent.goal_programming
        ]
        for radio in radio_buttons:
            radio.setEnabled(True)
            radio.setStyleSheet("")
        # Reset tables
        self.parent.var_restrictions_table.setRowCount(0)
        self.parent.priority_table.setRowCount(0)
        
        # Reset window size
        self.parent.resize(450, 350)
        self.parent.center_window()

    def on_restriction_change(self, checked):
        if checked:
            try:
                vars_count = int(self.parent.var_count.text())
                self.parent.table_manager.setup_var_restrictions_table(vars_count)
                self.parent.var_restrictions_table.show()
                self.parent.var_restrictions_label.show()
            except ValueError:
                pass
        else:
            self.parent.var_restrictions_table.hide()
            self.parent.var_restrictions_label.hide()

    def on_goal_programming_change(self, checked):
        if checked:
            try:
                constraints_count = int(self.parent.constraint_count.text())
                self.parent.table_manager.setup_priority_table(constraints_count)
                self.parent.priority_table.show()
                self.parent.priority_label.show()
            except ValueError:
                pass
        else:
            self.parent.priority_table.hide()
            self.parent.priority_label.hide()

    def update_window_size(self):
        # Base sizes
        base_width = 500  
        base_height = 200  # Reduced base height to prevent extra space
        print("update_window_size")

        # Dynamic width calculation based on number of variables
        if hasattr(self.parent, 'obj_table'):
            num_cols = self.parent.obj_table.columnCount()
            width = max(base_width, 120 + (num_cols * 90))  # Adjusted column width
        else:
            width = base_width

        # Dynamic height calculation based on number of constraints
        table_spacing = 5  # Reduced space between tables
        height = base_height

        if hasattr(self.parent, 'obj_table'):
            height += 60  # Objective function table height

        if hasattr(self.parent, 'constraint_table'):
            num_rows = self.parent.constraint_table.rowCount()
            height += (num_rows * 35) + table_spacing  # Reduced row height

        if hasattr(self.parent, 'var_restrictions_table'):
            height += 50 + table_spacing  # Reduced height for variable restrictions

        if hasattr(self.parent, 'priority_table'):
            height += 50 + table_spacing  # Reduced height for priority table

        # Extra padding for safety
        width += 40
        # height += 30  # Reduced extra height padding

        # Resize and center window
        self.parent.resize(width, height)
        self.parent.center_window()


