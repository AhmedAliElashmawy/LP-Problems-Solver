from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QScrollArea, QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        # Clear existing widgets from layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Create scroll area for the content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)
        
        # Add steps
        steps_frame = QFrame()
        steps_layout = QVBoxLayout(steps_frame)
        steps_label = QLabel("Solution Steps:")
        steps_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        steps_layout.addWidget(steps_label)
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setFont(QFont("Segoe UI", 11))
            steps_layout.addWidget(step_label)
            
        # Add final answer
        answer_label = QLabel(final_answer)
        answer_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        steps_layout.addWidget(answer_label)
        
        # Add back button
        back_btn = QPushButton("Back to Input")
        back_btn.clicked.connect(self.go_back)
        
        # Add everything to main layout
        self.layout.addWidget(scroll)
        self.layout.addWidget(steps_frame)
        self.layout.addWidget(back_btn)

    def go_back(self):
        self.hide()
        if self.parent():
            self.parent().show_input_widgets()
