from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QScrollArea, QPushButton, QFrame,
                           QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from io import StringIO
import pandas as pd
from .latex_renderer import LatexRenderer

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

    def display_native_solution(self, content_widget, steps, final_answer, is_twophase=False, is_goalprogramming=False, NumGoals=1):
        # Clear previous content
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
            
        # Add the problem formulation
        self.layout.addWidget(content_widget)
        
        # Create compact scroll area for LaTeX answers
        latex_scroll = QScrollArea()
        latex_scroll.setWidgetResizable(True)
        latex_scroll.setFixedHeight(120)  # Fixed compact height
        latex_content = QWidget()
        latex_layout = QVBoxLayout(latex_content)
        latex_scroll.setWidget(latex_content)
        
        # Format and display final answer first
        if final_answer and steps:
            answer_label = QLabel("Final Answer:")
            answer_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            latex_layout.addWidget(answer_label)
            
            last_step = steps[-1]
            if(is_goalprogramming):
                first_column = [line.split()[0] for line in last_step.split('\n')[1:len(last_step.split('\n'))-NumGoals]]
                last_column = [line.split()[-1] for line in last_step.split('\n')[1:]]
                for i in range(NumGoals):
                    z_value = last_column[-1-i]
                    latex_answer = z_value + r" \text{ at } ("
                    latex_assignments = [f"{first_column[i]} = {last_column[i]}" for i in range(len(first_column))]
                    latex_answer += ", ".join(latex_assignments) + ")"
                    self.latex(latex_answer, latex_layout, True, NumGoals-i, z_value)
            else:
                first_column = [line.split()[0] for line in last_step.split('\n')[1:-1]]
                last_column = [line.split()[-1] for line in last_step.split('\n')[1:]]
                z_value = last_column[-1]
                latex_answer = z_value + r" \text{ at } ("
                latex_assignments = [f"{first_column[i]} = {last_column[i]}" for i in range(len(first_column))]
                latex_answer += ", ".join(latex_assignments) + ")"
                self.latex(latex_answer, latex_layout, False, 0, z_value)
            print(first_column, last_column)
        
        # Add the LaTeX scroll area to main layout
        self.layout.addWidget(latex_scroll)
        self.layout.addWidget(self.create_separator())
            
        # Create scroll area for tables
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Add a "Solution Steps:" label
        steps_label = QLabel("Solution Steps:")
        steps_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        scroll_layout.addWidget(steps_label)
        
        if steps:
            first_step_lines = steps[0].split('\n')
            if first_step_lines:
                # Process headers once
                if is_twophase:
                    headers = steps[1].split('\n')[0].split()
                    phase_two_detected = False
                else:
                    headers = first_step_lines[0].split()
                
                # Process each step
                for step_index, step in enumerate(steps):
                    # Check for Phase II transition in two-phase method
                    if is_twophase:
                        if "PHASE II" in step:
                            phase_two_detected = True
                            # Create Phase II header
                            phase_label = QLabel("PHASE II")
                            phase_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                            scroll_layout.addWidget(phase_label)
                            temp = step_index
                            continue  # Skip this step as it's just the phase marker
                        
                        # Add Phase I label before the first step
                        if step_index == 0:
                            phase_label = QLabel("PHASE I")
                            phase_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                            scroll_layout.addWidget(phase_label)
                            continue  # Skip this step as it's just the phase marker
                    
                    # Create step label with appropriate numbering
                    if is_twophase:
                        if phase_two_detected:
                            headers = steps[step_index].split('\n')[0].split()
                            step_label = QLabel(f"Step {step_index - temp}:")
                        else:
                            step_label = QLabel(f"Step {step_index}:")
                    else:
                        step_label = QLabel(f"Step {step_index + 1}:")
                    
                    step_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                    scroll_layout.addWidget(step_label)
                    
                    # Create table for this step
                    table = QTableWidget()
                    table.setFont(QFont("Courier New", 12))  # Increased font size
                    table.verticalHeader().setVisible(False)
                    table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                    
                    # Process step data
                    lines = [line.strip() for line in step.split('\n') if line.strip()]
                    data_lines = lines[1:]  # Skip header line
                    table.setRowCount(len(data_lines))
                    
                    # Set dynamic minimum height (40 pixels per row plus header)
                    row_height = 40
                    header_height = 32
                    min_height = ((len(data_lines)) * row_height) + header_height
                    table.setMinimumHeight(min_height)
                    
                    # Set up table columns
                    table.setColumnCount(len(headers) + 1)
                    display_headers = ["---"] + headers
                    table.setHorizontalHeaderLabels(display_headers)
                    
                    # Add data to table
                    for row, line in enumerate(data_lines):
                        values = line.split()
                        if values:
                            # Fill columns
                            for col in range(len(values) - 1):
                                item = QTableWidgetItem(values[col])
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                table.setItem(row, col, item)
                            
                            # Add RHS value
                            if len(values) > 0:
                                rhs_item = QTableWidgetItem(values[-1])
                                rhs_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                table.setItem(row, len(headers), rhs_item)
                    
                    # Format table
                    table.horizontalHeader().setStretchLastSection(True)
                    for col in range(table.columnCount()):
                        table.setColumnWidth(col, 100)
                    
                    # Add table to scroll layout
                    scroll_layout.addWidget(table)
                    
                    # Add separator if not the last step
                    if step_index < len(steps) - 1:
                        scroll_layout.addWidget(self.create_separator())

        scroll_area.setWidget(scroll_content)
        self.layout.addWidget(scroll_area)

        # Add back button
        back_btn = QPushButton("Back to Input")
        back_btn.clicked.connect(self.go_back)
        self.layout.addWidget(back_btn)

    def is_non_zero(self, value):
        """Check if a value is non-zero, handling both numeric and algebraic expressions."""
        try:
            # Try converting to float first
            return float(value.strip()) != 0
        except ValueError:
            # If it contains algebraic expressions, check if it's not just "0"
            return value.strip() != "0"

    def latex(self, latex_answer, parent_layout, is_goalprogramming=False, goal_number=0, z_value='0'):
        answer_pixmap = LatexRenderer.render_lp_problem("", [latex_answer], [], is_goalprogramming, goal_number)
            
        answer_label = QLabel()
        answer_label.setPixmap(answer_pixmap)
        answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set dark background if z_value is not zero
        if is_goalprogramming and self.is_non_zero(z_value):
            answer_label.setStyleSheet("background-color: #0F0F0F;")
        
        parent_layout.addWidget(answer_label)

    def go_back(self):
        self.hide()
        if self.parent():
            self.parent().show_input_widgets()
