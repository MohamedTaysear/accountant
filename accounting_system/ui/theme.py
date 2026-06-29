import traceback
from PySide6.QtWidgets import (
    QLabel, QGraphicsDropShadowEffect, QStyledItemDelegate,
    QTableWidget, QAbstractItemView, QStyle,
    QAbstractScrollArea, QSizePolicy, QHeaderView,
)
from PySide6.QtCore import Qt, QPointF, QTimer, Property
from PySide6.QtGui import QPainter, QFont, QColor

class ThemeDefinition:
    is_dark = False
    # Colors
    primary = ""
    primary_hover = ""
    primary_pressed = ""
    success = ""
    warning = ""
    error = ""
    background = ""
    surface = ""
    surface_alt = ""
    surface_hover = ""
    border = ""
    border_focus = ""
    text_primary = ""
    text_secondary = ""
    text_disabled = ""
    text_placeholder = ""
    nav_bg = ""
    nav_text = ""
    nav_active = ""
    nav_active_bg = ""
    header_bg = ""
    
    # Typography
    font_family = ""
    size_normal = 0
    size_small = 0
    size_section = 0
    size_kpi_value = 0
    size_kpi_label = 0
    size_heading = 0
    size_page_title = 0
    
    # Spacing (8px Grid System)
    spacing_xs = 0
    spacing_sm = 0
    spacing_md = 0
    spacing_lg = 0
    spacing_xl = 0
    spacing_xxl = 0
    
    # Component constants
    card_border_radius = 0
    input_border_radius = 0
    button_border_radius = 0
    table_row_height = 0
    shadow_blur = 0
    shadow_offset_y = 0
    nav_active_bar_width = 0
    sidebar_width = 0


class LightTheme(ThemeDefinition):
    is_dark = False
    # Colors
    primary = "#2563EB"
    primary_hover = "#1D4ED8"
    primary_pressed = "#1E40AF"
    success = "#22C55E"
    warning = "#F59E0B"
    error = "#EF4444"
    background = "#F8FAFC"
    surface = "#FFFFFF"
    surface_alt = "#F1F5F9"
    surface_hover = "#E2E8F0"
    border = "#E2E8F0"
    border_focus = "#3B82F6"
    text_primary = "#1E293B"
    text_secondary = "#64748B"
    text_disabled = "#94A3B8"
    text_placeholder = "#94A3B8"
    nav_bg = "#FFFFFF"
    nav_text = "#64748B"
    nav_active = "#2563EB"
    nav_active_bg = "#EFF6FF"
    header_bg = "#F8FAFC"

    # Typography
    font_family = "Segoe UI Variable, Segoe UI, Inter, sans-serif"
    size_normal = 10
    size_small = 9
    size_section = 11
    size_kpi_value = 24
    size_kpi_label = 9
    size_heading = 13
    size_page_title = 18

    # Spacing (8px grid)
    spacing_xs = 4
    spacing_sm = 8
    spacing_md = 16
    spacing_lg = 24
    spacing_xl = 32
    spacing_xxl = 48

    # Component constants
    card_border_radius = 12
    input_border_radius = 8
    button_border_radius = 8
    table_row_height = 40
    shadow_blur = 15
    shadow_offset_y = 4
    nav_active_bar_width = 4
    sidebar_width = 240


class DarkTheme(ThemeDefinition):
    is_dark = True
    # Colors
    primary = "#3B82F6"
    primary_hover = "#60A5FA"
    primary_pressed = "#2563EB"
    success = "#22C55E"
    warning = "#F59E0B"
    error = "#EF4444"
    background = "#0F172A"
    surface = "#1E293B"
    surface_alt = "#334155"
    surface_hover = "#475569"
    border = "#334155"
    border_focus = "#60A5FA"
    text_primary = "#F8FAFC"
    text_secondary = "#94A3B8"
    text_disabled = "#64748B"
    text_placeholder = "#64748B"
    nav_bg = "#0F172A"
    nav_text = "#94A3B8"
    nav_active = "#60A5FA"
    nav_active_bg = "#1E293B"
    header_bg = "#0F172A"

    # Typography (Same as light)
    font_family = "Segoe UI Variable, Segoe UI, Inter, sans-serif"
    size_normal = 10
    size_small = 9
    size_section = 11
    size_kpi_value = 24
    size_kpi_label = 9
    size_heading = 13
    size_page_title = 18

    # Spacing (8px grid)
    spacing_xs = 4
    spacing_sm = 8
    spacing_md = 16
    spacing_lg = 24
    spacing_xl = 32
    spacing_xxl = 48

    # Component constants
    card_border_radius = 12
    input_border_radius = 8
    button_border_radius = 8
    table_row_height = 40
    shadow_blur = 25
    shadow_offset_y = 8
    nav_active_bar_width = 4
    sidebar_width = 240


_active: ThemeDefinition = LightTheme()

def set_theme(t: ThemeDefinition) -> None:
    global _active
    _active = t

class ElidingDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        text = index.data(Qt.DisplayRole) or ""
        elided = option.fontMetrics.elidedText(
            text, Qt.ElideRight, option.rect.width() - 2 * _active.spacing_md
        )
        painter.save()
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())
        
        # Center-left alignment with padding
        rect = option.rect.adjusted(_active.spacing_md, 0, -_active.spacing_md, 0)
        painter.drawText(rect, Qt.AlignVCenter | Qt.AlignLeft, elided)
        painter.restore()


def build_app_stylesheet() -> str:
    t = _active
    return f"""
/* ── Base ───────────────────────────────────────────────────── */
QWidget {{
    background-color: {t.background};
    font-family: "{t.font_family}";
    font-size: {t.size_normal}pt;
    color: {t.text_primary};
}}

QMainWindow, QDialog {{
    background-color: {t.background};
}}

/* ── Group Boxes ─────────────────────────────────────────────── */
QGroupBox {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {t.card_border_radius}px;
    margin-top: 24px;
    padding: {t.spacing_md}px;
    font-size: {t.size_section}pt;
    font-weight: bold;
    color: {t.text_primary};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: {t.spacing_md}px;
    top: -2px;
    padding: 0 {t.spacing_sm}px;
    background-color: {t.background};
    color: {t.primary};
    font-size: {t.size_small}pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* ── Buttons ─────────────────────────────────────────────────── */
QPushButton {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {t.button_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_md}px;
    min-height: 36px;
    color: {t.text_primary};
    font-size: {t.size_normal}pt;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {t.surface_alt};
    border-color: {t.primary};
    color: {t.primary};
}}
QPushButton:pressed {{
    background-color: {t.surface_hover};
}}
QPushButton:disabled {{
    color: {t.text_disabled};
    background-color: {t.surface_alt};
    border-color: {t.border};
}}

QPushButton[class="primary"] {{
    background-color: {t.primary};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}
QPushButton[class="primary"]:hover {{
    background-color: {t.primary_hover};
    border: none;
    color: #FFFFFF;
}}
QPushButton[class="primary"]:pressed {{
    background-color: {t.primary_pressed};
}}
QPushButton[class="primary"]:disabled {{
    background-color: {t.border};
    color: {t.text_disabled};
}}

QPushButton[class="destructive"] {{
    background-color: {t.error};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}
QPushButton[class="destructive"]:hover {{
    background-color: #DC2626;
}}
QPushButton[class="destructive"]:pressed {{
    background-color: #B91C1C;
}}

/* ── Inputs ──────────────────────────────────────────────────── */
QLineEdit, QComboBox, QDateEdit, QDateTimeEdit, QDoubleSpinBox, QSpinBox {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_md}px;
    min-height: 38px;
    background-color: {t.surface};
    color: {t.text_primary};
    selection-background-color: {t.primary};
    selection-color: white;
}}
QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QDateTimeEdit:hover, QDoubleSpinBox:hover, QSpinBox:hover {{
    border-color: {t.text_disabled};
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
    border: 2px solid {t.primary};
    padding: {t.spacing_sm - 1}px {t.spacing_md - 1}px; /* Adjust padding for thicker border */
    background-color: {t.surface};
}}
QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled, QDateTimeEdit:disabled, QDoubleSpinBox:disabled, QSpinBox:disabled {{
    background-color: {t.surface_alt};
    color: {t.text_disabled};
    border-color: {t.border};
}}

QComboBox::drop-down, QDateEdit::drop-down, QDateTimeEdit::drop-down {{
    border: none;
    width: 32px;
}}
QComboBox::down-arrow {{
    width: 14px;
    height: 14px;
}}
QComboBox QAbstractItemView {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    background-color: {t.surface};
    color: {t.text_primary};
    selection-background-color: {t.surface_alt};
    selection-color: {t.text_primary};
    padding: 4px;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    min-height: 32px;
    padding: 8px 12px;
    border-radius: 4px;
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {t.surface_hover};
}}

QDoubleSpinBox::up-button, QSpinBox::up-button,
QDoubleSpinBox::down-button, QSpinBox::down-button {{
    border: none;
    width: 24px;
    background: transparent;
}}

/* ── Tables ──────────────────────────────────────────────────── */
QTableWidget, QTableView, QTreeView {{
    background-color: {t.surface};
    alternate-background-color: {t.surface_alt};
    border: 1px solid {t.border};
    border-radius: {t.card_border_radius}px;
    selection-background-color: {t.nav_active_bg};
    selection-color: {t.primary};
    color: {t.text_primary};
    outline: none;
    gridline-color: transparent;
}}
QTableWidget::item, QTableView::item, QTreeView::item {{
    padding: {t.spacing_sm}px {t.spacing_md}px;
    border-bottom: 1px solid {t.border};
}}
QTableWidget::item:selected, QTableView::item:selected, QTreeView::item:selected {{
    background-color: {t.nav_active_bg};
    color: {t.primary};
}}
QTableWidget::item:hover, QTableView::item:hover, QTreeView::item:hover {{
    background-color: {t.surface_hover};
}}

QHeaderView {{
    background-color: {t.surface};
    border-top-left-radius: {t.card_border_radius}px;
    border-top-right-radius: {t.card_border_radius}px;
}}
QHeaderView::section {{
    background-color: {t.surface};
    border: none;
    border-bottom: 2px solid {t.border};
    padding: {t.spacing_md}px;
    font-weight: 600;
    color: {t.text_secondary};
    font-size: {t.size_small}pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    qproperty-alignment: AlignLeft | AlignVCenter;
}}
QHeaderView::section:checked {{
    background-color: {t.surface};
}}

/* ── Scrollbars ──────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {t.text_disabled};
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t.text_secondary};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    border: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: {t.text_disabled};
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {t.text_secondary};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    border: none;
}}

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle {{
    background: {t.border};
}}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}

/* ── CheckBox ────────────────────────────────────────────────── */
QCheckBox {{
    color: {t.text_primary};
    spacing: {t.spacing_sm}px;
    min-height: 30px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {t.border};
    border-radius: 4px;
    background-color: {t.surface};
}}
QCheckBox::indicator:checked {{
    background-color: {t.primary};
    border-color: {t.primary};
    image: url(none); /* Setup a custom SVG checkmark here if desired */
}}
QCheckBox::indicator:hover {{
    border-color: {t.primary};
}}

/* ── Tool Tips ───────────────────────────────────────────────── */
QToolTip {{
    background-color: {t.surface};
    color: {t.text_primary};
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: 6px 12px;
    font-size: {t.size_small}pt;
    opacity: 230;
}}

/* ── Message Boxes ───────────────────────────────────────────── */
QMessageBox {{
    background-color: {t.surface};
    border-radius: {t.card_border_radius}px;
}}
QMessageBox QLabel {{
    color: {t.text_primary};
    background-color: transparent;
}}

/* ── Menus ───────────────────────────────────────────────────── */
QMenu {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: 8px;
    padding: {t.spacing_xs}px;
}}
QMenu::item {{
    padding: {t.spacing_sm}px {t.spacing_xl}px;
    border-radius: 4px;
    color: {t.text_primary};
    margin: 2px;
}}
QMenu::item:selected {{
    background-color: {t.nav_active_bg};
    color: {t.primary};
}}
QMenu::separator {{
    height: 1px;
    background: {t.border};
    margin: 4px 8px;
}}

/* ── Scroll Area ─────────────────────────────────────────────── */
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* ── Labels ──────────────────────────────────────────────────── */
QLabel {{
    color: {t.text_primary};
    background: transparent;
}}

/* ── Form Layout labels ──────────────────────────────────────── */
QFormLayout QLabel {{
    color: {t.text_secondary};
    font-size: {t.size_normal}pt;
    font-weight: 500;
    background: transparent;
}}

/* ── Text areas ──────────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_md}px;
    background-color: {t.surface};
    color: {t.text_primary};
    selection-background-color: {t.primary};
    selection-color: white;
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {t.primary};
    padding: {t.spacing_sm - 1}px {t.spacing_md - 1}px;
}}
QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {t.surface_alt};
    color: {t.text_disabled};
}}

/* ── Menu Bar ────────────────────────────────────────────────── */
QMenuBar {{
    background-color: {t.surface};
    color: {t.text_primary};
    border-bottom: 1px solid {t.border};
}}
QMenuBar::item {{
    padding: 6px 16px;
    background: transparent;
    color: {t.text_primary};
}}
QMenuBar::item:selected {{
    background-color: {t.surface_alt};
    color: {t.primary};
}}
QMenuBar::item:pressed {{
    background-color: {t.border};
}}
"""


_TABLE_MIN_HEIGHT = 70
_TABLE_MAX_HEIGHT = 420
_TABLE_HEADER_H   = 44

_ACTIONS_COL_WIDTH  = 240
_BTN_MIN_EDIT       = 60
_BTN_MIN_DELETE     = 65
_BTN_MIN_DEACTIVATE = 90
_BTN_MIN_ACTIVATE   = 75
_BTN_MIN_REMOVE     = 75


def _fit_table_height(table: QTableWidget, max_h: int) -> None:
    row_h     = table.verticalHeader().defaultSectionSize()
    hdr_h     = table.horizontalHeader().sizeHint().height() or _TABLE_HEADER_H
    content_h = hdr_h + table.rowCount() * row_h + 2
    new_h     = max(_TABLE_MIN_HEIGHT, min(content_h, max_h))
    table.setFixedHeight(new_h)


def apply_actions_column(table: QTableWidget, col: int) -> None:
    table.setColumnWidth(col, _ACTIONS_COL_WIDTH)
    table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)


def apply_table_style(table: QTableWidget, max_height: int = _TABLE_MAX_HEIGHT) -> None:
    table.setAlternatingRowColors(True)
    table.verticalHeader().setDefaultSectionSize(_active.table_row_height)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(False) # Modern tables hide internal grids
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setMinimumSectionSize(100)
    table.setItemDelegate(ElidingDelegate(table))
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _resize(*_):
        QTimer.singleShot(0, lambda: _fit_table_height(table, max_height))

    m = table.model()
    m.rowsInserted.connect(_resize)
    m.rowsRemoved.connect(_resize)
    m.modelReset.connect(_resize)
    QTimer.singleShot(0, lambda: _fit_table_height(table, max_height))


def make_empty_label(message: str) -> QLabel:
    lbl = QLabel(message)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setMinimumHeight(100)
    font = QFont(_active.font_family, _active.size_normal)
    font.setItalic(False)
    lbl.setFont(font)
    lbl.setStyleSheet(
        f"color: {_active.text_secondary}; font-weight: 500; background: transparent;"
    )
    return lbl


def make_card_shadow() -> QGraphicsDropShadowEffect:
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(_active.shadow_blur)
    shadow.setOffset(QPointF(0, _active.shadow_offset_y))
    shadow.setColor(QColor(0, 0, 0, 40 if _active.is_dark else 15))
    return shadow


def color_for_value(value: float) -> str:
    if value > 0:
        return _active.success
    if value < 0:
        return _active.error
    return _active.text_primary


def make_section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {_active.size_section}pt;"
        f" font-weight: 700;"
        f" color: {_active.text_primary};"
        f" background: transparent;"
        f" padding: 0;"
        f" margin: 0;")
    return lbl


def make_page_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {_active.size_page_title}pt;"
        f" font-weight: 700;"
        f" color: {_active.text_primary};"
        f" background: transparent;")
    return lbl


def card_frame_style() -> str:
    t = _active
    return (f"background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px;")
