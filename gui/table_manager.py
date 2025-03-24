from PyQt6.QtWidgets import QTableWidgetItem, QComboBox, QLineEdit
from PyQt6.QtCore import Qt
try:
    from .styles import setup_styles
except ImportError:
    from styles import setup_styles  # Adjust for absolute import if relative fails

class TableManager:
    def __init__(self, parent):
        self.parent = parent
        
    def create_tables(self):
        try:
            vars_count = int(self.parent.var_count.text())
            constraints_count = int(self.parent.constraint_count.text())
            if(not self.parent.goal_programming.isChecked()):
                self.setup_objective_table(vars_count)
            self.setup_constraints_table(vars_count, constraints_count)
            
            if self.parent.unrestricted_radio.isChecked():
                self.setup_var_restrictions_table(vars_count)
                self.parent.var_restrictions_table.show()
                self.parent.var_restrictions_label.show()
        except ValueError:
            pass

    def setup_objective_table(self, vars_count):
        self.parent.obj_table.setRowCount(1)
        self.parent.obj_table.setColumnCount(vars_count)
        self.parent.obj_table.setFixedWidth(min(800, self.parent.width() - 40))  # Dynamic width
        self.parent.obj_table.setFixedHeight(88)
        self.parent.obj_table.horizontalHeader().setStretchLastSection(True)
        self.parent.obj_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        obj_header_item = QTableWidgetItem("z")
        self.parent.obj_table.setVerticalHeaderItem(0, obj_header_item)
        
        for i in range(vars_count):
            var_name = f"x{i+1}"
            self.parent.obj_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("Enter coefficient")
            self.parent.obj_table.setCellWidget(0, i, line_edit)
        self.parent.obj_table.horizontalHeader().sectionDoubleClicked.connect(lambda index: self.edit_header(index, vars_count))

    def setup_constraints_table(self, vars_count, constraints_count):
        self.parent.constraint_table.setRowCount(constraints_count)
        self.parent.constraint_table.setColumnCount(vars_count + 2)
        self.parent.constraint_table.setFixedWidth(min(800, self.parent.width() - 40))  # Dynamic width
        
        # Stretch all columns to fill the available space
        header = self.parent.constraint_table.horizontalHeader()
        for i in range(vars_count + 2):
            header.setSectionResizeMode(i, header.ResizeMode.Stretch)
        
        # Calculate dynamic height based on number of rows
        row_height = 40
        header_height = 50
        table_height = (constraints_count * row_height) + header_height
        self.parent.constraint_table.setMinimumHeight(table_height)
        self.parent.constraint_table.setMaximumHeight(table_height)
        
        for i in range(vars_count):
            var_name = f"x{i+1}"
            self.parent.constraint_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))
            
        relation_header = QTableWidgetItem("Relation")
        rhs_header = QTableWidgetItem("RHS")
        self.parent.constraint_table.setHorizontalHeaderItem(vars_count, relation_header)
        self.parent.constraint_table.setHorizontalHeaderItem(vars_count + 1, rhs_header)
        
        for i in range(constraints_count):
            # Set row height
            self.parent.constraint_table.setRowHeight(i, row_height)
            
            for j in range(vars_count):
                line_edit = QLineEdit()
                line_edit.setPlaceholderText("Enter coefficient")
                self.parent.constraint_table.setCellWidget(i, j, line_edit)
            relation_combo = QComboBox()
            if(self.parent.simplex_radio.isChecked()):
                relation_combo.addItems(["≤"])
            else:
                relation_combo.addItems(["≤", "=", "≥"])
            self.parent.constraint_table.setCellWidget(i, vars_count, relation_combo)
            rhs_line_edit = QLineEdit()
            rhs_line_edit.setPlaceholderText("Enter RHS value")
            self.parent.constraint_table.setCellWidget(i, vars_count + 1, rhs_line_edit)

    def setup_var_restrictions_table(self, vars_count):
        self.parent.var_restrictions_table.setRowCount(1)
        self.parent.var_restrictions_table.setColumnCount(vars_count)
        self.parent.var_restrictions_table.setFixedWidth(min(800, self.parent.width() - 40))  # Dynamic width
        self.parent.var_restrictions_table.setFixedHeight(88)
        self.parent.var_restrictions_table.horizontalHeader().setStretchLastSection(True)
        
        for i in range(vars_count):
            var_name = self.parent.obj_table.horizontalHeaderItem(i).text() if self.parent.obj_table.horizontalHeaderItem(i) else f"x{i+1}"
            self.parent.var_restrictions_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))
            
            combo = QComboBox()
            combo.addItems(["Unrestricted", "≥ 0"])
            self.parent.var_restrictions_table.setCellWidget(0, i, combo)

    def setup_priority_table(self, constraints_count):
        self.parent.priority_table.setRowCount(1)
        self.parent.priority_table.setColumnCount(constraints_count)
        self.parent.priority_table.setFixedWidth(min(800, self.parent.width() - 40))  # Dynamic width
        self.parent.priority_table.setFixedHeight(88)
        self.parent.priority_table.horizontalHeader().setStretchLastSection(True)
        
        for i in range(constraints_count):
            var_name = f"C{i+1}"  # Changed to use constraint numbers instead of variable names
            self.parent.priority_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))
            
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("Enter priority")
            self.parent.priority_table.setCellWidget(0, i, line_edit)

    def edit_header(self, index, vars_count):
        old_text = self.parent.obj_table.horizontalHeaderItem(index).text()
        
        line_edit = QLineEdit(old_text, self.parent.obj_table)
        line_edit.setFrame(False)
        line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_edit.setGeometry(
            self.parent.obj_table.horizontalHeader().sectionPosition(index) + 40, 
            11,
            self.parent.obj_table.horizontalHeader().sectionSize(index), 
            self.parent.obj_table.horizontalHeader().height()
        )
        line_edit.editingFinished.connect(lambda: self.update_header(index, line_edit, vars_count))
        line_edit.setFocus()
        line_edit.show()

    def update_header(self, index, line_edit, vars_count):
        new_text = line_edit.text().strip()
        if new_text:
            # Update headers in all tables
            self.parent.obj_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
            self.parent.constraint_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
            if hasattr(self.parent, 'priority_table'):
                self.parent.priority_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
            if self.parent.unrestricted_radio.isChecked():
                self.parent.var_restrictions_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
        line_edit.deleteLater()
