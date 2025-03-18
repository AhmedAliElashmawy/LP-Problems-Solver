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
        self.parent.unrestricted_radio.toggled.connect(self.on_restriction_change)
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
        
        # Connect goal programming
        self.parent.goal_programming.toggled.connect(self.on_goal_programming_change)

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

        # Add priority table (but keep hidden by default)
        self.parent.layout.addWidget(self.parent.priority_label)
        self.parent.layout.addWidget(self.parent.priority_table)
        self.parent.priority_label.hide()
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
            self.parent.priority_table, self.parent.priority_label
        ]
        for widget in widgets:
            widget.hide()

    def on_create_tables(self):
        self.parent.resize(800, 800)  # Increased height to accommodate priority table
        self.parent.center_window()
        self.parent.table_manager.create_tables()
        
        # Disable inputs
        self.parent.var_count.setEnabled(False)
        self.parent.constraint_count.setEnabled(False)
        self.parent.non_negative_radio.setEnabled(False)
        self.parent.unrestricted_radio.setEnabled(False)
        self.parent.simplex_radio.setEnabled(False)
        self.parent.bigm_radio.setEnabled(False)
        self.parent.twophase_radio.setEnabled(False)
        self.parent.goal_programming.setEnabled(False)
        
        # Show widgets
        widgets = [
            self.parent.min_radio, self.parent.obj_table, self.parent.obj_label,
            self.parent.constraint_label, self.parent.constraint_table,
            self.parent.solve_btn, self.parent.clear_btn
        ]
        for widget in widgets:
            widget.show()
            
        self.parent.create_tables_btn.hide()
        
        if self.parent.goal_programming.isChecked():
            try:
                vars_count = int(self.parent.var_count.text())
                self.parent.table_manager.setup_priority_table(vars_count)
                self.parent.priority_table.show()
                self.parent.priority_label.show()
            except ValueError:
                pass

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
        self.parent.non_negative_radio.setEnabled(True)
        self.parent.unrestricted_radio.setEnabled(True)
        self.parent.simplex_radio.setEnabled(True)
        self.parent.bigm_radio.setEnabled(True)
        self.parent.twophase_radio.setEnabled(True)
        self.parent.goal_programming.setEnabled(True)
        
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
        if checked and self.parent.obj_table.columnCount() > 0:
            vars_count = self.parent.obj_table.columnCount()
            self.parent.table_manager.setup_priority_table(vars_count)
            self.parent.priority_table.show()
            self.parent.priority_label.show()
        else:
            self.parent.priority_table.hide()
            self.parent.priority_label.hide()
