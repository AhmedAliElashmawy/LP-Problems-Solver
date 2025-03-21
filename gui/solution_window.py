from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QScrollArea, QPushButton, QFrame,
                           QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from io import StringIO
import pandas as pd

class SolutionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setWindowTitle("Solution")  # Add window title
        self.resize(800, 800)  # Set default size

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create scrollable area for solution steps
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)

        # Input summary section
        self.input_label = QLabel("Problem Input:")
        self.input_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.input_content = QLabel()
        self.input_content.setWordWrap(True)

        # Solution steps section
        self.steps_label = QLabel("Solution Steps:")
        self.steps_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.steps_content = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_content)

        # Final answer section
        self.answer_label = QLabel("Final Answer:")
        self.answer_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.answer_content = QLabel()
        self.answer_content.setWordWrap(True)

        # Back button
        self.back_button = QPushButton("Back to Input")
        self.back_button.clicked.connect(self.go_back)

        # Add widgets to layout
        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.input_content)
        self.layout.addWidget(self.create_separator())
        self.layout.addWidget(self.steps_label)
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.create_separator())
        self.layout.addWidget(self.answer_label)
        self.layout.addWidget(self.answer_content)
        self.layout.addWidget(self.back_button)

        self.setWindowFlags(Qt.WindowType.Window)  # Make it an independent window

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def display_solution(self, input_data, steps, final_answer):
        self.input_content.setText(input_data)
        
        # Clear previous steps
        for i in reversed(range(self.steps_layout.count())): 
            self.steps_layout.itemAt(i).widget().setParent(None)
        
        # Add new steps
        for step in steps:
            step_label = QLabel(step)
            step_label.setWordWrap(True)
            self.steps_layout.addWidget(step_label)
        
        self.answer_content.setText(final_answer)

    def display_native_solution(self, content_widget, steps, final_answer):
        # Clear previous content
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
            
        # Add the problem formulation
        self.layout.addWidget(content_widget)
        
        # Create table for steps
        table = QTableWidget()
        table.setFont(QFont("Courier New", 10))
        table.verticalHeader().setVisible(False)  # Hide row numbers
        
        if steps:
            first_step_lines = steps[0].split('\n')
            if first_step_lines:
                # Process headers
                headers = first_step_lines[0].split()
                
                # Set up table with all columns including RHS
                table.setColumnCount(len(headers) + 1)
                display_headers = ["---"] + headers  # Create a new list with "---" prepended
                table.setHorizontalHeaderLabels(display_headers)
                
                # Populate table with all steps
                current_row = 0
                for step in steps:
                    lines = [line.strip() for line in step.split('\n') if line.strip()]
                    data_lines = lines[1:]  # Skip header line
                    table.setRowCount(table.rowCount() + len(data_lines))
                    
                    # Add step data
                    for line in data_lines:
                        values = line.split()
                        if values:  # Only process if we have values
                            # Fill the shifted columns (all except last value)
                            for j in range(len(values) - 1):
                                item = QTableWidgetItem(values[j])
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                table.setItem(current_row, j, item)
                            
                            # Add the last value as RHS in the last column
                            if len(values) > 0:
                                rhs_item = QTableWidgetItem(values[-1])
                                rhs_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                table.setItem(current_row, len(headers), rhs_item)
                        
                        current_row += 1
                    
                    # Add separator row if not the last step
                    if step != steps[-1]:
                        table.setRowCount(table.rowCount() + 1)
                        for j in range(len(headers) + 1):  # +1 for the extra column
                            if j == 0:  # First column should display step number
                                step_number = f"step{steps.index(step) + 1}"
                                item = QTableWidgetItem(step_number)
                            else:
                                item = QTableWidgetItem("---")
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            table.setItem(current_row, j, item)
                        current_row += 1
        
        # Format final answer from the last line of the last step
        if steps:
            last_step = steps[-1]
            last_line = last_step.split('\n')[-1].strip()
            values = last_line.split()
            
            if values:
                # Extract z value (last value)
                z_value = values[-1]
                
                # Create variable assignments string
                var_assignments = []
                for i, header in enumerate(headers[:-1], 1):
                    if i < len(values):
                        var_assignments.append(f"{header}={values[i]}")
                
                # Format final answer in LaTeX
                latex_answer = z_value + r" \text{ at } ("
                latex_assignments = [f"{header}={values[i]}" for i, header in enumerate(headers[:-1], 1) if i < len(values)]
                latex_answer += ", ".join(latex_assignments) + ")"
                
                # Create a single line LaTeX expression for the final answer
                # Remove the extra '$' signs since render_lp_problem already adds them
                from .latex_renderer import LatexRenderer
                answer_pixmap = LatexRenderer.render_lp_problem("", [latex_answer], [])

        # Adjust table properties
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        
        # Add everything to main layout in new order
        if final_answer:
            answer_label = QLabel("Final Answer:")
            answer_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.layout.addWidget(answer_label)
            
            # Create label for the LaTeX rendered answer
            answer_label = QLabel()
            answer_label.setPixmap(answer_pixmap)
            answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(answer_label)

        self.layout.addWidget(table)
        
        # Add back button
        back_btn = QPushButton("Back to Input")
        back_btn.clicked.connect(self.go_back)
        self.layout.addWidget(back_btn)

    def go_back(self):
        self.hide()
        if self.parent():
            self.parent().show_input_widgets()
