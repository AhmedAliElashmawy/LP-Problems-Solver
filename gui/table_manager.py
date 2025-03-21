from PyQt6.QtWidgets import QTableWidgetItem, QComboBox, QLineEdit
from PyQt6.QtCore import Qt

class TableManager:
    def __init__(self, parent):
        self.parent = parent
        
    def create_tables(self):
        try:
            vars_count = int(self.parent.var_count.text())
            constraints_count = int(self.parent.constraint_count.text())
            
            self.setup_objective_table(vars_count)
            self.setup_constraints_table(vars_count, constraints_count)
            
            if self.parent.unrestricted_radio.isChecked():
                self.setup_var_restrictions_table(vars_count)
                
        except ValueError:
            pass

    def setup_objective_table(self, vars_count):
        self.parent.obj_table.setRowCount(1)
        self.parent.obj_table.setColumnCount(vars_count)
        self.parent.obj_table.setFixedSize(800, 68)
        
        obj_header_item = QTableWidgetItem("z")
        self.parent.obj_table.setVerticalHeaderItem(0, obj_header_item)
        
        for i in range(vars_count):
            var_name = f"x{i+1}"
            self.parent.obj_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))

    def setup_constraints_table(self, vars_count, constraints_count):
        self.parent.constraint_table.setRowCount(constraints_count)
        self.parent.constraint_table.setColumnCount(vars_count + 2)
        
        for i in range(vars_count):
            var_name = f"x{i+1}"
            self.parent.constraint_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))
            
        relation_header = QTableWidgetItem("Relation")
        rhs_header = QTableWidgetItem("RHS")
        self.parent.constraint_table.setHorizontalHeaderItem(vars_count, relation_header)
        self.parent.constraint_table.setHorizontalHeaderItem(vars_count + 1, rhs_header)
        
        for i in range(constraints_count):
            relation_combo = QComboBox()
            relation_combo.addItems(["<=", "=", ">="])
            self.parent.constraint_table.setCellWidget(i, vars_count, relation_combo)

    def setup_var_restrictions_table(self, vars_count):
        self.parent.var_restrictions_table.setRowCount(1)
        self.parent.var_restrictions_table.setColumnCount(vars_count)
        self.parent.var_restrictions_table.setFixedSize(800, 68)
        
        for i in range(vars_count):
            var_name = self.parent.obj_table.horizontalHeaderItem(i).text() if self.parent.obj_table.horizontalHeaderItem(i) else f"x{i+1}"
            self.parent.var_restrictions_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))
            
            combo = QComboBox()
            combo.addItems(["Unrestricted", "≥ 0", "≤ 0"])
            self.parent.var_restrictions_table.setCellWidget(0, i, combo)

    def setup_priority_table(self, vars_count):
        self.parent.priority_table.setRowCount(1)
        self.parent.priority_table.setColumnCount(vars_count)
        
        for i in range(vars_count):
            var_name = self.parent.obj_table.horizontalHeaderItem(i).text() if self.parent.obj_table.horizontalHeaderItem(i) else f"x{i+1}"
            self.parent.priority_table.setHorizontalHeaderItem(i, QTableWidgetItem(var_name))
            
            combo = QComboBox()
            combo.addItems(["P1", "P2", "P3", "P4", "P5"])
            self.parent.priority_table.setCellWidget(0, i, combo)

    def edit_header(self, index, vars_count):
        old_text = self.parent.obj_table.horizontalHeaderItem(index).text()
        
        line_edit = QLineEdit(old_text, self.parent.obj_table)
        line_edit.setFrame(False)
        line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_edit.setGeometry(
            self.parent.obj_table.horizontalHeader().sectionPosition(index) + 28, 
            0,
            self.parent.obj_table.horizontalHeader().sectionSize(index), 
            self.parent.obj_table.horizontalHeader().height()
        )
        line_edit.editingFinished.connect(lambda: self.update_header(index, line_edit, vars_count))
        line_edit.setFocus()
        line_edit.show()

    def update_header(self, index, line_edit, vars_count):
        new_text = line_edit.text().strip()
        if new_text:
            self.parent.obj_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
            self.parent.constraint_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
            if self.parent.unrestricted_radio.isChecked():
                self.parent.var_restrictions_table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
        line_edit.deleteLater()
