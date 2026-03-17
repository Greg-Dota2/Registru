import os
import sys
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QLineEdit, QTextEdit,
    QComboBox, QDateEdit, QFileDialog, QTableWidget, QTableWidgetItem,
    QMessageBox, QFrame, QHeaderView, QButtonGroup, QSizePolicy,
    QScrollArea, QAbstractItemView,
)

from pathlib import Path

# Resolve the app's root directory whether running as .py or compiled .exe
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent          # writable dir next to .exe
    BUNDLE_DIR = Path(sys._MEIPASS)                # bundled read-only assets
else:
    APP_DIR = Path(__file__).parent
    BUNDLE_DIR = APP_DIR

from database import DatabaseManager
from models.document import Document
from utils.exporter import export_to_excel, export_to_pdf
from utils.file_utils import backup_database, copy_attachment, resolve_attachment
from ui.style import STYLE_SHEET


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #475569; background: transparent;")
    return lbl


_INPUT_STYLE = """
    border: 1.5px solid #dde3ee;
    border-radius: 7px;
    padding: 7px 10px;
    background-color: #ffffff;
    color: #2d3748;
    font-size: 13px;
    font-family: 'Segoe UI', Arial, sans-serif;
"""

_COMBOBOX_STYLE = _INPUT_STYLE + """
    QComboBox::drop-down { border: none; width: 28px; }
    QComboBox:focus { border-color: #2563eb; }
    QComboBox QAbstractItemView {
        border: 1.5px solid #dde3ee;
        background: white;
        color: #1e293b;
        selection-background-color: #2563eb;
        selection-color: white;
        outline: none;
        padding: 4px;
    }
    QComboBox QAbstractItemView::item {
        padding: 7px 10px;
        min-height: 28px;
        color: #1e293b;
        background: transparent;
    }
    QComboBox QAbstractItemView::item:hover {
        background-color: #eff6ff;
        color: #1e293b;
    }
"""


def style_input(widget) -> None:
    """Apply input styling directly on a widget so parent stylesheets can't interfere."""
    from PySide6.QtWidgets import QComboBox as _CB, QDateEdit as _DE
    if isinstance(widget, _CB):
        widget.setStyleSheet("QComboBox {" + _COMBOBOX_STYLE + "}")
    elif isinstance(widget, _DE):
        widget.setStyleSheet(
            "QDateEdit {" + _INPUT_STYLE + "}"
            "QDateEdit:focus { border-color: #2563eb; }"
            "QDateEdit::drop-down { border: none; width: 28px; }"
        )
    else:
        widget.setStyleSheet(
            type(widget).__name__ + " {" + _INPUT_STYLE + "}"
            + type(widget).__name__ + ":focus { border-color: #2563eb; }"
        )


def make_btn(text: str, style: str, height: int = 36) -> QPushButton:
    """Create a QPushButton with inline styles so parent stylesheets can't interfere."""
    _styles = {
        'primary': {
            'bg': '#2563eb', 'hover': '#1d4ed8', 'pressed': '#1e40af',
            'color': 'white', 'border': '#1d4ed8',
        },
        'danger': {
            'bg': '#ef4444', 'hover': '#dc2626', 'pressed': '#b91c1c',
            'color': 'white', 'border': '#dc2626',
        },
        'success': {
            'bg': '#059669', 'hover': '#047857', 'pressed': '#065f46',
            'color': 'white', 'border': '#047857',
        },
        'secondary': {
            'bg': '#dbeafe', 'hover': '#bfdbfe', 'pressed': '#bfdbfe',
            'color': '#1d4ed8', 'border': '#93c5fd',
        },
        'ghost': {
            'bg': '#f1f5f9', 'hover': '#e8f0fe', 'pressed': '#dbeafe',
            'color': '#334155', 'border': '#cbd5e1',
        },
    }
    s = _styles[style]
    btn = QPushButton(text)
    btn.setFixedHeight(height)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {s['bg']};
            color: {s['color']};
            border-radius: 8px;
            padding: 6px 16px;
            font-weight: bold;
            border: 1.5px solid {s['border']};
            font-size: 13px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QPushButton:hover {{
            background-color: {s['hover']};
        }}
        QPushButton:pressed {{
            background-color: {s['pressed']};
        }}
    """)
    return btn


def make_card(radius: int = 12) -> QFrame:
    card = QFrame()
    card.setStyleSheet(f"QFrame {{ background: white; border-radius: {radius}px; }}")
    return card


# ---------------------------------------------------------------------------
# Stat Card widget
# ---------------------------------------------------------------------------

class StatCard(QFrame):
    def __init__(self, title: str, value: str, accent: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: white; border-radius: 12px; }}")
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # Colored left accent strip
        strip = QFrame()
        strip.setFixedWidth(5)
        strip.setStyleSheet(f"background: {accent}; border-top-left-radius: 12px; border-bottom-left-radius: 12px;")
        row.addWidget(strip)

        # Content
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(18, 16, 20, 14)
        layout.setSpacing(4)

        self._value_lbl = QLabel(value)
        self._value_lbl.setStyleSheet(
            f"font-size: 34px; font-weight: bold; color: {accent};"
        )
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #94a3b8; letter-spacing: 1px;"
        )

        layout.addWidget(self._value_lbl)
        layout.addWidget(title_lbl)
        row.addWidget(content)

    def update_value(self, value: str):
        self._value_lbl.setText(value)


# ---------------------------------------------------------------------------
# Document Form page
# ---------------------------------------------------------------------------

class DocumentForm(QScrollArea):
    def __init__(self, db: DatabaseManager, on_saved=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.on_saved = on_saved
        self.edit_doc_id = None

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("QScrollArea { background: #f0f2f7; border: none; }")

        inner = QWidget()
        inner.setObjectName("formInner")
        inner.setStyleSheet("QWidget#formInner { background: #f0f2f7; }")
        self.setWidget(inner)

        outer = QVBoxLayout(inner)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.setSpacing(18)

        # Page title
        self._page_title = QLabel("Adaugă document nou")
        self._page_title.setStyleSheet(
            "font-size: 21px; font-weight: bold; color: #1e293b; background: transparent;"
        )
        outer.addWidget(self._page_title)

        # --- Card ---
        card = make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 28)
        card_layout.setSpacing(18)

        # Row 1: Tip | Data | Tip document
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        col_tip = QVBoxLayout()
        col_tip.setSpacing(6)
        col_tip.addWidget(field_label("Tip Intrare / Ieșire"))
        self.tip_inout = QComboBox()
        self.tip_inout.addItems(["Intrare", "Ieșire"])
        style_input(self.tip_inout)
        col_tip.addWidget(self.tip_inout)

        col_data = QVBoxLayout()
        col_data.setSpacing(6)
        col_data.addWidget(field_label("Data"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        style_input(self.date_edit)
        col_data.addWidget(self.date_edit)

        col_tipdoc = QVBoxLayout()
        col_tipdoc.setSpacing(6)
        col_tipdoc.addWidget(field_label("Tip document"))
        self.tip_document = QComboBox()
        self.tip_document.addItems(["Factura", "Contract", "Cerere", "Aviz", "Notificare", "Alte"])
        style_input(self.tip_document)
        col_tipdoc.addWidget(self.tip_document)

        row1.addLayout(col_tip, 1)
        row1.addLayout(col_data, 1)
        row1.addLayout(col_tipdoc, 1)
        card_layout.addLayout(row1)

        # Row 2: Număr document | Emitent/Destinatar
        row2 = QHBoxLayout()
        row2.setSpacing(20)

        col_nr = QVBoxLayout()
        col_nr.setSpacing(6)
        col_nr.addWidget(field_label("Număr document"))
        self.numar_document = QLineEdit()
        self.numar_document.setPlaceholderText("ex: Factură 1234")
        style_input(self.numar_document)
        col_nr.addWidget(self.numar_document)

        col_emit = QVBoxLayout()
        col_emit.setSpacing(6)
        col_emit.addWidget(field_label("Emitent / Destinatar"))
        self.emitent_destinatar = QLineEdit()
        self.emitent_destinatar.setPlaceholderText("Numele firmei sau persoanei")
        style_input(self.emitent_destinatar)
        col_emit.addWidget(self.emitent_destinatar)

        row2.addLayout(col_nr, 1)
        row2.addLayout(col_emit, 1)
        card_layout.addLayout(row2)

        # Descriere
        col_desc = QVBoxLayout()
        col_desc.setSpacing(6)
        col_desc.addWidget(field_label("Descriere"))
        self.descriere = QTextEdit()
        self.descriere.setPlaceholderText("Descriere scurtă a documentului...")
        self.descriere.setFixedHeight(80)
        col_desc.addWidget(self.descriere)
        card_layout.addLayout(col_desc)

        # Observații
        col_obs = QVBoxLayout()
        col_obs.setSpacing(6)
        col_obs.addWidget(field_label("Observații"))
        self.observatii = QTextEdit()
        self.observatii.setPlaceholderText("Observații suplimentare...")
        self.observatii.setFixedHeight(70)
        col_obs.addWidget(self.observatii)
        card_layout.addLayout(col_obs)

        # Attachment
        col_attach = QVBoxLayout()
        col_attach.setSpacing(6)
        col_attach.addWidget(field_label("Fișier atașat  (opțional)"))
        attach_row = QHBoxLayout()
        attach_row.setSpacing(10)
        self.attachment_path = QLineEdit()
        self.attachment_path.setReadOnly(True)
        self.attachment_path.setPlaceholderText("Niciun fișier selectat")
        self.btn_attach = make_btn("Selectează fișier", "ghost")
        self.btn_attach.setFixedWidth(150)
        self.btn_attach.clicked.connect(self._browse_file)
        attach_row.addWidget(self.attachment_path)
        attach_row.addWidget(self.btn_attach)
        col_attach.addLayout(attach_row)
        card_layout.addLayout(col_attach)

        outer.addWidget(card)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_save = make_btn("Salvează document", "primary", height=40)
        self.btn_save.clicked.connect(self._save_document)

        self.btn_clear = make_btn("Resetează formularul", "ghost", height=40)
        self.btn_clear.clicked.connect(self.clear_form)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_save)
        outer.addLayout(btn_row)
        outer.addStretch()

    # -- public API --

    def clear_form(self):
        self.edit_doc_id = None
        self._page_title.setText("Adaugă document nou")
        self.tip_inout.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())
        self.numar_document.clear()
        self.tip_document.setCurrentIndex(0)
        self.emitent_destinatar.clear()
        self.descriere.clear()
        self.observatii.clear()
        self.attachment_path.clear()
        self.btn_save.setText("Salvează document")

    def set_document(self, doc: Document):
        self.edit_doc_id = doc.id
        self._page_title.setText(f"Editează document  #{doc.id}")
        self.tip_inout.setCurrentText(doc.tip_inout)
        self.date_edit.setDate(QDate.fromString(doc.data, "yyyy-MM-dd"))
        self.numar_document.setText(doc.numar_document)
        self.tip_document.setCurrentText(doc.tip_document)
        self.emitent_destinatar.setText(doc.emitent_destinatar)
        self.descriere.setPlainText(doc.descriere)
        self.observatii.setPlainText(doc.observatii)
        self.attachment_path.setText(doc.attachment_path or "")
        self.btn_save.setText("Actualizează document")

    # -- private --

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selectează fișier atașat", "",
            "Documente (*.pdf *.png *.jpg *.jpeg *.bmp *.gif);;Toate fișierele (*.*)",
        )
        if path:
            subfolder = self.tip_document.currentText()
            rel_path = copy_attachment(path, APP_DIR / "attachments", subfolder)
            self.attachment_path.setText(rel_path)

    def _save_document(self):
        tip_inout = self.tip_inout.currentText()
        data = self.date_edit.date().toString("yyyy-MM-dd")
        numar_document = self.numar_document.text().strip()
        tip_document = self.tip_document.currentText()
        emitent_destinatar = self.emitent_destinatar.text().strip()
        descriere = self.descriere.toPlainText().strip()
        observatii = self.observatii.toPlainText().strip()
        attachment_path = self.attachment_path.text().strip() or None

        if not numar_document:
            QMessageBox.warning(self, "Validare", "Introduceți numărul documentului.")
            return
        if not emitent_destinatar:
            QMessageBox.warning(self, "Validare", "Introduceți Emitent / Destinatar.")
            return

        if self.edit_doc_id:
            self.db.update_document(
                self.edit_doc_id, tip_inout, data, numar_document,
                tip_document, emitent_destinatar, descriere, observatii, attachment_path,
            )
            QMessageBox.information(self, "Succes", "Document actualizat cu succes!")
        else:
            self.db.add_document(
                tip_inout, data, numar_document, tip_document,
                emitent_destinatar, descriere, observatii, attachment_path,
            )
            QMessageBox.information(self, "Succes", "Document adăugat cu succes!")

        self.clear_form()
        if self.on_saved:
            self.on_saved()


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registru Intrări-Ieșiri")
        self.setMinimumSize(1060, 680)
        self.setGeometry(120, 80, 1320, 820)

        icon_path = BUNDLE_DIR / "assets" / "icon.jpg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.db = DatabaseManager()
        self.db.create_tables()

        self._init_ui()
        self.setStyleSheet(STYLE_SHEET)
        self.refresh_dashboard()
        self.load_document_list()

    # -----------------------------------------------------------------------
    # Layout construction
    # -----------------------------------------------------------------------

    def _init_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_content_area(), 1)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(228)
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 75, 16, 20)
        layout.setSpacing(0)

        divider = QFrame()
        divider.setObjectName("sidebarDivider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        layout.addSpacing(14)

        # Navigation
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._nav_group.buttonClicked.connect(
            lambda btn: self._switch_page(self._nav_group.id(btn))
        )

        nav_items = [
            ("  Dashboard", 0),
            ("  Adaugă document", 1),
            ("  Listă documente", 2),
        ]
        self._nav_buttons = []
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._nav_group.addButton(btn, idx)
            layout.addWidget(btn)
            layout.addSpacing(4)
            self._nav_buttons.append(btn)

        self._nav_buttons[0].setChecked(True)

        layout.addSpacing(14)

        # Logo image below nav buttons
        logo_path = BUNDLE_DIR / "assets" / "logo.png"
        if logo_path.exists():
            logo_lbl = QLabel()
            pixmap = QPixmap(str(logo_path))
            logo_lbl.setPixmap(
                pixmap.scaledToWidth(190, Qt.TransformationMode.SmoothTransformation)
            )
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_lbl.setStyleSheet("background: transparent; padding: 4px 0px 8px 0px;")
            layout.addWidget(logo_lbl)

        layout.addStretch()

        ver = QLabel("v1.0.0")
        ver.setObjectName("sidebarVersion")
        layout.addWidget(ver)

        return sidebar

    def _build_content_area(self) -> QWidget:
        area = QWidget()
        area.setObjectName("contentArea")
        area.setStyleSheet("QWidget#contentArea { background: #f0f2f7; }")
        layout = QVBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._page_stack = QStackedWidget()
        self._page_stack.setObjectName("pageStack")
        self._page_stack.setStyleSheet("QStackedWidget#pageStack { background: #f0f2f7; }")
        self._page_stack.addWidget(self._build_dashboard_page())   # 0
        self._document_form = DocumentForm(self.db, on_saved=self._on_document_saved)
        self._page_stack.addWidget(self._document_form)            # 1
        self._page_stack.addWidget(self._build_list_page())        # 2

        layout.addWidget(self._page_stack)
        return area

    # -----------------------------------------------------------------------
    # Dashboard page
    # -----------------------------------------------------------------------

    def _build_dashboard_page(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #f0f2f7; border: none; }")

        page = QWidget()
        page.setObjectName("dashboardPage")
        page.setStyleSheet("QWidget#dashboardPage { background: #f0f2f7; }")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(22)

        title = QLabel("Dashboard")
        title.setStyleSheet(
            "font-size: 21px; font-weight: bold; color: #1e293b; background: transparent;"
        )
        layout.addWidget(title)

        # Stat cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(18)
        self._card_total = StatCard("Total Documente", "0", "#2563eb")
        self._card_intrari = StatCard("Intrări", "0", "#059669")
        self._card_iesiri = StatCard("Ieșiri", "0", "#d97706")
        cards_row.addWidget(self._card_total)
        cards_row.addWidget(self._card_intrari)
        cards_row.addWidget(self._card_iesiri)
        layout.addLayout(cards_row)

        # Recent documents
        recent_card = make_card()
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        recent_layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 12)
        sec_title = QLabel("Documente recente")
        sec_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1e293b; background: transparent;"
        )
        header_layout.addWidget(sec_title)
        header_layout.addStretch()
        btn_view_all = make_btn("Vezi toate →", "ghost", height=32)
        btn_view_all.clicked.connect(lambda: self._switch_page(2))
        header_layout.addWidget(btn_view_all)
        recent_layout.addWidget(header)

        self._recent_table = self._make_table(
            ["Nr.", "Tip", "Data", "Tip document", "Nr. document", "Emitent / Destinatar"]
        )
        self._recent_table.setMaximumHeight(280)
        recent_layout.addWidget(self._recent_table)

        layout.addWidget(recent_card)
        layout.addStretch()

        scroll.setWidget(page)
        return scroll

    # -----------------------------------------------------------------------
    # Document list page
    # -----------------------------------------------------------------------

    def _build_list_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("listPage")
        page.setStyleSheet("QWidget#listPage { background: #f0f2f7; }")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 20)
        layout.setSpacing(16)

        title = QLabel("Listă documente")
        title.setStyleSheet(
            "font-size: 21px; font-weight: bold; color: #1e293b; background: transparent;"
        )
        layout.addWidget(title)

        # Filter bar card
        filter_card = make_card(10)
        fl = QHBoxLayout(filter_card)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(14)

        for lbl in ("De la:", "Până la:"):
            l = QLabel(lbl)
            l.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold; background: transparent;")
            fl.addWidget(l)
            if lbl == "De la:":
                self._date_from = QDateEdit(QDate.currentDate().addMonths(-1))
                self._date_from.setDisplayFormat("yyyy-MM-dd")
                self._date_from.setCalendarPopup(True)
                self._date_from.setFixedWidth(128)
                style_input(self._date_from)
                fl.addWidget(self._date_from)
            else:
                self._date_to = QDateEdit(QDate.currentDate())
                self._date_to.setDisplayFormat("yyyy-MM-dd")
                self._date_to.setCalendarPopup(True)
                self._date_to.setFixedWidth(128)
                style_input(self._date_to)
                fl.addWidget(self._date_to)

        tip_lbl = QLabel("Tip:")
        tip_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold; background: transparent;")
        fl.addWidget(tip_lbl)
        self._filter_type = QComboBox()
        self._filter_type.addItems(["Toate", "Intrare", "Ieșire"])
        self._filter_type.setFixedWidth(110)
        style_input(self._filter_type)
        fl.addWidget(self._filter_type)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Caută după număr, emitent, descriere...")
        self._search_input.returnPressed.connect(self.load_document_list)
        style_input(self._search_input)
        fl.addWidget(self._search_input)

        btn_search = make_btn("Caută", "primary")
        btn_search.setFixedWidth(80)
        btn_search.clicked.connect(self.load_document_list)
        fl.addWidget(btn_search)

        layout.addWidget(filter_card)

        # Table card
        table_card = make_card(10)
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(0)

        self._table = self._make_table([
            "Nr.", "Tip", "Data", "Tip document",
            "Nr. document", "Emitent / Destinatar", "Descriere", "Atașament",
        ])
        self._table.setSortingEnabled(True)
        tc_layout.addWidget(self._table)

        layout.addWidget(table_card, 1)

        # Action buttons row
        actions = QHBoxLayout()
        actions.setSpacing(8)

        btn_edit = make_btn("  Editează", "secondary")
        btn_edit.clicked.connect(self._edit_selected)

        btn_delete = make_btn("  Șterge", "danger")
        btn_delete.clicked.connect(self._delete_selected)

        btn_attach = make_btn("  Deschide atașament", "ghost")
        btn_attach.clicked.connect(self._open_attachment)

        btn_xlsx = make_btn("  Export Excel", "success")
        btn_xlsx.clicked.connect(self._export_xlsx)

        btn_pdf = make_btn("  Export PDF", "ghost")
        btn_pdf.clicked.connect(self._export_pdf)

        btn_backup = make_btn("  Backup DB", "ghost")
        btn_backup.clicked.connect(self._backup_db)

        actions.addWidget(btn_edit)
        actions.addWidget(btn_delete)
        actions.addWidget(btn_attach)
        actions.addStretch()
        actions.addWidget(btn_xlsx)
        actions.addWidget(btn_pdf)
        actions.addWidget(btn_backup)

        layout.addLayout(actions)
        return page

    # -----------------------------------------------------------------------
    # Shared table factory
    # -----------------------------------------------------------------------

    def _make_table(self, headers: list) -> QTableWidget:
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)
        tbl.setShowGrid(False)
        tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return tbl

    # -----------------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------------

    def _switch_page(self, index: int):
        self._page_stack.setCurrentIndex(index)
        self._nav_buttons[index].setChecked(True)
        if index == 0:
            self.refresh_dashboard()
        elif index == 2:
            self.load_document_list()

    # -----------------------------------------------------------------------
    # Data refresh
    # -----------------------------------------------------------------------

    def refresh_dashboard(self):
        stats = self.db.get_stats()
        self._card_total.update_value(str(stats["total"]))
        self._card_intrari.update_value(str(stats["intrari"]))
        self._card_iesiri.update_value(str(stats["iesiri"]))

        rows = self.db.get_recent_documents(12)
        self._recent_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self._recent_table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self._recent_table.setItem(i, 1, self._tip_item(row["tip_inout"]))
            self._recent_table.setItem(i, 2, QTableWidgetItem(row["data"]))
            self._recent_table.setItem(i, 3, self._tipdoc_item(row["tip_document"]))
            self._recent_table.setItem(i, 4, QTableWidgetItem(row["numar_document"]))
            self._recent_table.setItem(i, 5, QTableWidgetItem(row["emitent_destinatar"]))
        self._recent_table.resizeRowsToContents()

    def load_document_list(self):
        tip = self._filter_type.currentText()
        date_from = self._date_from.date().toString("yyyy-MM-dd")
        date_to = self._date_to.date().toString("yyyy-MM-dd")
        search = self._search_input.text().strip()

        docs = self.db.get_documents(
            tip_inout=tip if tip != "Toate" else None,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )

        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(docs))
        for i, doc in enumerate(docs):
            self._table.setItem(i, 0, QTableWidgetItem(str(doc["id"])))
            self._table.setItem(i, 1, self._tip_item(doc["tip_inout"]))
            self._table.setItem(i, 2, QTableWidgetItem(doc["data"]))
            self._table.setItem(i, 3, self._tipdoc_item(doc["tip_document"]))
            self._table.setItem(i, 4, QTableWidgetItem(doc["numar_document"]))
            self._table.setItem(i, 5, QTableWidgetItem(doc["emitent_destinatar"]))
            self._table.setItem(i, 6, QTableWidgetItem(doc["descriere"]))

            has_attach = doc["attachment_path"]
            attach_item = QTableWidgetItem("Da" if has_attach else "—")
            if has_attach:
                attach_item.setForeground(QColor("#2563eb"))
            else:
                attach_item.setForeground(QColor("#94a3b8"))
            self._table.setItem(i, 7, attach_item)
        self._table.setSortingEnabled(True)
        self._table.resizeRowsToContents()

    # -----------------------------------------------------------------------
    # Table helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _tip_item(tip: str) -> QTableWidgetItem:
        item = QTableWidgetItem(tip)
        item.setForeground(
            QColor("#059669") if tip == "Intrare" else QColor("#1e3a8a")
        )
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        return item

    _TIPDOC_COLORS = {
        "Factura":    "#d97706",  # amber
        "Contract":   "#7c3aed",  # purple
        "Cerere":     "#2563eb",  # blue
        "Aviz":       "#0891b2",  # teal
        "Notificare": "#db2777",  # pink
        "Alte":       "#64748b",  # slate
    }

    @classmethod
    def _tipdoc_item(cls, tip: str) -> QTableWidgetItem:
        item = QTableWidgetItem(tip)
        color = cls._TIPDOC_COLORS.get(tip, "#64748b")
        item.setForeground(QColor(color))
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        return item

    def _get_selected_doc(self) -> Document | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selecție", "Selectați un document din listă.")
            return None
        doc_id = int(self._table.item(rows[0].row(), 0).text())
        return self.db.get_document_by_id(doc_id)

    # -----------------------------------------------------------------------
    # Actions
    # -----------------------------------------------------------------------

    def _on_document_saved(self):
        self.refresh_dashboard()
        self.load_document_list()

    def _edit_selected(self):
        doc = self._get_selected_doc()
        if doc:
            self._switch_page(1)
            self._document_form.set_document(doc)

    def _delete_selected(self):
        doc = self._get_selected_doc()
        if not doc:
            return
        confirm = QMessageBox.question(
            self, "Confirmare ștergere",
            f"Ștergi documentul  #{doc.id} — {doc.numar_document}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.delete_document(doc.id)
            if doc.attachment_path:
                file_path = resolve_attachment(doc.attachment_path, APP_DIR)
                if file_path.exists():
                    file_path.unlink()
            self.load_document_list()
            self.refresh_dashboard()

    def _open_attachment(self):
        doc = self._get_selected_doc()
        if not doc:
            return
        if not doc.attachment_path:
            QMessageBox.information(self, "Atașament", "Documentul nu are fișier atașat.")
            return
        full_path = resolve_attachment(doc.attachment_path, APP_DIR)
        if full_path.exists():
            os.startfile(str(full_path))
        else:
            QMessageBox.warning(self, "Eroare", f"Fișierul nu a fost găsit:\n{full_path}")

    def _export_xlsx(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvează Excel", "registru.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        docs = self.db.get_documents()
        export_to_excel(docs, path)
        QMessageBox.information(self, "Export reușit", f"Fișier salvat:\n{path}")

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvează PDF", "registru.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        docs = self.db.get_documents()
        export_to_pdf(docs, path)
        QMessageBox.information(self, "Export reușit", f"Fișier salvat:\n{path}")

    def _backup_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Backup bază de date", "registru_backup.db", "SQLite DB (*.db)"
        )
        if not path:
            return
        backup_database(self.db.db_path, path)
        QMessageBox.information(self, "Backup reușit", f"Backup salvat:\n{path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Registru Intrări-Ieșiri")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
