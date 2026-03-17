STYLE_SHEET = """
/* ===== Global ===== */
* {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QWidget {
    color: #2d3748;
}
QMainWindow {
    background-color: #f0f2f7;
}
/* Labels are transparent so they show their parent's background */
QLabel {
    background: transparent;
    color: #2d3748;
}

/* ===== Sidebar ===== */
#sidebar {
    background-color: #16213e;
}
#appTitle {
    color: #ffffff;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 2px;
    background: transparent;
}
#appSubtitle {
    color: #8aa3c8;
    font-size: 11px;
    background: transparent;
}
#sidebarDivider {
    background-color: #1e2d50;
    max-height: 1px;
    border: none;
}
#navBtn {
    background: transparent;
    color: #c0cfe8;
    text-align: left;
    padding: 11px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
    border: none;
}
#navBtn:hover {
    background-color: rgba(255, 255, 255, 0.10);
    color: #ffffff;
}
#navBtn:checked {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
}
#sidebarVersion {
    color: #5e7a9e;
    font-size: 11px;
}

/* ===== Input Controls ===== */
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    border: 1.5px solid #dde3ee;
    border-radius: 7px;
    padding: 7px 10px;
    background-color: #ffffff;
    color: #2d3748;
    selection-background-color: #2563eb;
    selection-color: white;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border-color: #2563eb;
}
QLineEdit:read-only {
    background-color: #f8fafc;
    color: #94a3b8;
}
QLineEdit::placeholder, QTextEdit::placeholder {
    color: #94a3b8;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox QAbstractItemView {
    border: 1.5px solid #dde3ee;
    border-radius: 6px;
    background: white;
    color: #1e293b;
    padding: 4px;
    selection-background-color: #2563eb;
    selection-color: white;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 6px 10px;
    border-radius: 4px;
    min-height: 28px;
    color: #1e293b;
    background: transparent;
}
QDateEdit::drop-down {
    border: none;
    width: 28px;
}
QCalendarWidget {
    background: white;
}
QCalendarWidget QAbstractItemView {
    border: none;
}

/* ===== Buttons ===== */
QPushButton#primaryBtn {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: bold;
    border: 1px solid #1d4ed8;
}
QPushButton#primaryBtn:hover { background-color: #1d4ed8; border-color: #1e40af; }
QPushButton#primaryBtn:pressed { background-color: #1e40af; }

QPushButton#dangerBtn {
    background-color: #ef4444;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: bold;
    border: 1px solid #dc2626;
}
QPushButton#dangerBtn:hover { background-color: #dc2626; border-color: #b91c1c; }
QPushButton#dangerBtn:pressed { background-color: #b91c1c; }

QPushButton#secondaryBtn {
    background-color: #dbeafe;
    color: #1d4ed8;
    border-radius: 8px;
    padding: 8px 18px;
    border: 1.5px solid #93c5fd;
    font-weight: bold;
}
QPushButton#secondaryBtn:hover { background-color: #bfdbfe; }

QPushButton#ghostBtn {
    background-color: #f1f5f9;
    color: #334155;
    border-radius: 8px;
    padding: 8px 16px;
    border: 1.5px solid #cbd5e1;
    font-weight: bold;
}
QPushButton#ghostBtn:hover {
    background-color: #e8f0fe;
    color: #2563eb;
    border-color: #93c5fd;
}

QPushButton#successBtn {
    background-color: #059669;
    color: white;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    border: 1px solid #047857;
}
QPushButton#successBtn:hover { background-color: #047857; border-color: #065f46; }

/* ===== Table ===== */
QTableWidget {
    background-color: #ffffff;
    border: none;
    gridline-color: transparent;
    outline: none;
    alternate-background-color: #f8fafc;
}
QTableWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid #f1f5f9;
}
QTableWidget::item:selected {
    background-color: #eff6ff;
    color: #1e40af;
}
QTableWidget::item:hover {
    background-color: #f8fafc;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #94a3b8;
    font-weight: bold;
    font-size: 11px;
    padding: 10px 14px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    letter-spacing: 0.5px;
}
QHeaderView::section:first {
    border-top-left-radius: 0px;
}
QHeaderView {
    background: #f8fafc;
}

/* ===== Scrollbar ===== */
QScrollBar:vertical {
    background: transparent;
    width: 7px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 32px;
}
QScrollBar::handle:vertical:hover { background: #94a3b8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

QScrollBar:horizontal {
    background: transparent;
    height: 7px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 4px;
    min-width: 32px;
}
QScrollBar::handle:horizontal:hover { background: #94a3b8; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ===== Message Box ===== */
QMessageBox { background-color: white; }
QMessageBox QLabel { color: #374151; font-size: 13px; background: white; }
QMessageBox QPushButton {
    background-color: #2563eb;
    color: white;
    border-radius: 7px;
    padding: 7px 24px;
    border: none;
    min-width: 80px;
    font-weight: bold;
}
QMessageBox QPushButton:hover { background-color: #1d4ed8; }
QMessageBox QPushButton[text="No"], QMessageBox QPushButton[text="Cancel"],
QMessageBox QPushButton[text="&No"], QMessageBox QPushButton[text="&Cancel"] {
    background-color: #f1f5f9;
    color: #374151;
    border: 1.5px solid #e2e8f0;
}

/* ===== Tooltip ===== */
QToolTip {
    background-color: #1e293b;
    color: #f1f5f9;
    border: none;
    padding: 6px 10px;
    border-radius: 5px;
    font-size: 12px;
}
"""
