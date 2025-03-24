def setup_styles(window):
    window.setStyleSheet("""
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
    QTableWidget {
        background-color: #1C1C1C;
        gridline-color: #3A3A3A;
        border: 1px solid #3A3A3A;
        border-radius: 6px;
        margin: 10px;
    }
    QTableWidget::item {
        padding: 5px;
        # color: #E0E0E0;
        border: none;
    }
    QTableWidget QHeaderView::section {
        # background-color: #252526;
        # color: #E0E0E0;
        padding: 5px;
        border: 1px solid #3A3A3A;
    }
    QTableWidget QLineEdit, QTableWidget QComboBox {
        margin: 1px;
        min-height: 24px;
    }
    QTableWidget::item:selected {
        background-color: #007ACC;
    }
    QMessageBox {
        background-color: #1C1C1C;
        color: #D0D0D0;
        min-width: 400px;
        min-height: 150px;
    }
    QMessageBox QLabel {
        color: #D0D0D0;
        font-size: 14px;
        padding: 20px;
        min-width: 300px;
    }
    QMessageBox QPushButton {
        min-width: 100px;
        min-height: 30px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007ACC, stop:1 #005A9E);
        color: white;
        border: 1px solid #004C8C;
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 12px;
    }
    QMessageBox QPushButton:hover {
        background: #008CFF;
    }
    QMessageBox QPushButton:pressed {
        background: #005A9E;
    }
    """)