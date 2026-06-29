from PySide6.QtWidgets import (
    QLabel, QGraphicsDropShadowEffect, QStyledItemDelegate,
    QTableWidget, QAbstractItemView, QStyle,
    QAbstractScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QPainter, QFont, QColor


class ThemeDefinition:
    # Colors
    primary = ""
    primary_dark = ""
    success = ""
    success_light = ""
    warning = ""
    warning_light = ""
    error = ""
    error_light = ""
    background = ""
    surface = ""
    surface_alt = ""
    border = ""
    border_focus = ""
    text_primary = ""
    text_secondary = ""
    text_disabled = ""
    text_placeholder = ""
    nav_bg = ""
    nav_text = ""
    nav_active = ""
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
    # Spacing
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
    # Colors
    primary = "#2563EB"
    primary_dark = "#1D4ED8"
    success = "#16A34A"
    success_light = "#DCFCE7"
    warning = "#D97706"
    warning_light = "#FEF3C7"
    error = "#DC2626"
    error_light = "#FEE2E2"
    background = "#EEF2F7"
    surface = "#FFFFFF"
    surface_alt = "#F8FAFC"
    border = "#D1D9E6"
    border_focus = "#93C5FD"
    text_primary = "#1E293B"
    text_secondary = "#64748B"
    text_disabled = "#94A3B8"
    text_placeholder = "#94A3B8"
    nav_bg = "#1A2535"
    nav_text = "#94A3B8"
    nav_active = "#2563EB"
    header_bg = "#DDE3ED"
    # Typography
    font_family = "Segoe UI"
    size_normal = 10
    size_small = 9
    size_section = 10
    size_kpi_value = 20
    size_kpi_label = 9
    size_heading = 11
    size_page_title = 13
    # Spacing
    spacing_xs = 4
    spacing_sm = 8
    spacing_md = 12
    spacing_lg = 16
    spacing_xl = 24
    spacing_xxl = 32
    # Component constants
    card_border_radius = 8
    input_border_radius = 4
    button_border_radius = 4
    table_row_height = 30
    shadow_blur = 10
    shadow_offset_y = 2
    nav_active_bar_width = 3
    sidebar_width = 200


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
        painter.drawText(
            option.rect.adjusted(_active.spacing_md, 0, -_active.spacing_md, 0),
            Qt.AlignVCenter | Qt.AlignLeft,
            elided,
        )
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
    border-radius: 6px;
    margin-top: 14px;
    padding: 4px 2px 6px 2px;
    font-size: {t.size_section}pt;
    font-weight: bold;
    color: {t.text_primary};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: -1px;
    padding: 0 6px;
    background-color: {t.surface};
    color: {t.text_secondary};
    font-size: {t.size_small}pt;
    font-weight: bold;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* ── Buttons ─────────────────────────────────────────────────── */
QPushButton {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {t.button_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_lg}px;
    min-height: 30px;
    color: {t.text_primary};
    font-size: {t.size_normal}pt;
}}
QPushButton:hover {{
    background-color: {t.surface_alt};
    border-color: {t.primary};
    color: {t.primary};
}}
QPushButton:pressed {{
    background-color: {t.border};
}}
QPushButton:disabled {{
    color: {t.text_disabled};
    background-color: {t.surface_alt};
    border-color: {t.border};
}}

QPushButton[class="primary"] {{
    background-color: {t.primary};
    color: white;
    border: none;
    font-weight: bold;
}}
QPushButton[class="primary"]:hover {{
    background-color: {t.primary_dark};
}}
QPushButton[class="primary"]:pressed {{
    background-color: {t.primary_dark};
}}
QPushButton[class="primary"]:disabled {{
    background-color: {t.text_disabled};
    color: white;
}}

QPushButton[class="destructive"] {{
    background-color: {t.error};
    color: white;
    border: none;
    font-weight: bold;
}}
QPushButton[class="destructive"]:hover {{
    background-color: #B91C1C;
}}
QPushButton[class="destructive"]:pressed {{
    background-color: #991B1B;
}}

/* ── Inputs ──────────────────────────────────────────────────── */
QLineEdit {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_md}px;
    min-height: 30px;
    background-color: {t.surface};
    color: {t.text_primary};
    selection-background-color: {t.primary};
    selection-color: white;
}}
QLineEdit:focus {{
    border: 1px solid {t.border_focus};
    background-color: {t.surface};
}}
QLineEdit:disabled {{
    background-color: {t.surface_alt};
    color: {t.text_disabled};
    border-color: {t.border};
}}
QLineEdit:read-only {{
    background-color: {t.surface_alt};
    color: {t.text_secondary};
}}

QComboBox {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_md}px;
    min-height: 30px;
    background-color: {t.surface};
    color: {t.text_primary};
}}
QComboBox:focus {{
    border-color: {t.border_focus};
}}
QComboBox:disabled {{
    background-color: {t.surface_alt};
    color: {t.text_disabled};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}
QComboBox QAbstractItemView {{
    border: 1px solid {t.border};
    border-radius: 4px;
    background-color: {t.surface};
    color: {t.text_primary};
    selection-background-color: {t.primary};
    selection-color: white;
    padding: 2px;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    min-height: 26px;
    padding: 4px 8px;
}}

QDateEdit, QDateTimeEdit {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_md}px;
    min-height: 30px;
    background-color: {t.surface};
    color: {t.text_primary};
}}
QDateEdit:focus, QDateTimeEdit:focus {{
    border-color: {t.border_focus};
}}
QDateEdit::drop-down, QDateTimeEdit::drop-down {{
    border: none;
    width: 24px;
}}

QDoubleSpinBox, QSpinBox {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px {t.spacing_md}px;
    min-height: 30px;
    background-color: {t.surface};
    color: {t.text_primary};
}}
QDoubleSpinBox:focus, QSpinBox:focus {{
    border-color: {t.border_focus};
}}
QDoubleSpinBox:disabled, QSpinBox:disabled {{
    background-color: {t.surface_alt};
    color: {t.text_disabled};
}}
QDoubleSpinBox::up-button, QSpinBox::up-button,
QDoubleSpinBox::down-button, QSpinBox::down-button {{
    border: none;
    width: 18px;
    background: transparent;
}}

/* ── Tables ──────────────────────────────────────────────────── */
QTableWidget {{
    gridline-color: {t.border};
    background-color: {t.surface};
    alternate-background-color: {t.surface_alt};
    border: 1px solid {t.border};
    border-radius: 0px;
    selection-background-color: #DBEAFE;
    selection-color: {t.text_primary};
    outline: none;
}}
QTableWidget::item {{
    padding: {t.spacing_sm}px {t.spacing_md}px;
    color: {t.text_primary};
    border: none;
}}
QTableWidget::item:selected {{
    background-color: #DBEAFE;
    color: {t.text_primary};
}}
QTableWidget::item:hover {{
    background-color: #F0F7FF;
}}
QHeaderView {{
    background-color: {t.header_bg};
}}
QHeaderView::section {{
    background-color: {t.header_bg};
    border: none;
    border-bottom: 2px solid {t.border};
    border-right: 1px solid {t.border};
    padding: {t.spacing_sm}px {t.spacing_md}px;
    font-weight: bold;
    color: {t.text_secondary};
    font-size: {t.size_small}pt;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    qproperty-alignment: AlignLeft;
}}
QHeaderView::section:last {{
    border-right: none;
}}
QHeaderView::section:checked {{
    background-color: {t.header_bg};
}}

/* ── Scrollbars ──────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {t.surface_alt};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t.border};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t.text_disabled};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    border: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QScrollBar:horizontal {{
    background: {t.surface_alt};
    height: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {t.border};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {t.text_disabled};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    border: none;
}}

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle {{
    background: {t.border};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}

/* ── CheckBox ────────────────────────────────────────────────── */
QCheckBox {{
    color: {t.text_primary};
    spacing: {t.spacing_sm}px;
    min-height: 24px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {t.border};
    border-radius: 3px;
    background-color: {t.surface};
}}
QCheckBox::indicator:checked {{
    background-color: {t.primary};
    border-color: {t.primary};
}}
QCheckBox::indicator:hover {{
    border-color: {t.primary};
}}

/* ── Tool Tips ───────────────────────────────────────────────── */
QToolTip {{
    background-color: {t.nav_bg};
    color: #FFFFFF;
    border: 1px solid {t.nav_bg};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: {t.size_small}pt;
    opacity: 1;
}}

/* ── Message Boxes ───────────────────────────────────────────── */
QMessageBox {{
    background-color: {t.surface};
}}
QMessageBox QLabel {{
    color: {t.text_primary};
    background-color: transparent;
}}

/* ── Menus ───────────────────────────────────────────────────── */
QMenu {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    border-radius: 4px;
    color: {t.text_primary};
}}
QMenu::item:selected {{
    background-color: {t.primary};
    color: white;
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
    background: transparent;
}}

/* ── Text areas ──────────────────────────────────────────────── */
QTextEdit {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px;
    background-color: {t.surface};
    color: {t.text_primary};
    selection-background-color: {t.primary};
    selection-color: white;
}}
QTextEdit:focus {{
    border-color: {t.border_focus};
}}
QTextEdit:disabled {{
    background-color: {t.surface_alt};
    color: {t.text_disabled};
}}
QPlainTextEdit {{
    border: 1px solid {t.border};
    border-radius: {t.input_border_radius}px;
    padding: {t.spacing_sm}px;
    background-color: {t.surface};
    color: {t.text_primary};
    selection-background-color: {t.primary};
    selection-color: white;
}}
QPlainTextEdit:focus {{
    border-color: {t.border_focus};
}}
QPlainTextEdit:disabled {{
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
    padding: 4px 12px;
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

/* ── Table/Tree Views (non-QTableWidget) ─────────────────────── */
QTableView {{
    gridline-color: {t.border};
    background-color: {t.surface};
    alternate-background-color: {t.surface_alt};
    border: 1px solid {t.border};
    selection-background-color: #DBEAFE;
    selection-color: {t.text_primary};
    color: {t.text_primary};
    outline: none;
}}
QTableView::item {{
    padding: {t.spacing_sm}px {t.spacing_md}px;
    color: {t.text_primary};
    border: none;
}}
QTableView::item:selected {{
    background-color: #DBEAFE;
    color: {t.text_primary};
}}
QTableView::item:hover {{
    background-color: #F0F7FF;
    color: {t.text_primary};
}}
QTreeView {{
    background-color: {t.surface};
    alternate-background-color: {t.surface_alt};
    border: 1px solid {t.border};
    selection-background-color: #DBEAFE;
    selection-color: {t.text_primary};
    color: {t.text_primary};
    outline: none;
}}
QTreeView::item {{
    padding: {t.spacing_sm}px {t.spacing_md}px;
    color: {t.text_primary};
}}
QTreeView::item:selected {{
    background-color: #DBEAFE;
    color: {t.text_primary};
}}
QTreeView::item:hover {{
    background-color: #F0F7FF;
    color: {t.text_primary};
}}
"""


_TABLE_MIN_HEIGHT = 68   # header row height + a small margin
_TABLE_MAX_HEIGHT = 390  # ~12 data rows before vertical scroll starts
_TABLE_HEADER_H   = 36   # approximate header section height


def _fit_table_height(table: QTableWidget, max_h: int) -> None:
    """Set the table's fixed height to exactly fit its rows, capped at max_h."""
    row_h     = table.verticalHeader().defaultSectionSize()
    hdr_h     = table.horizontalHeader().sizeHint().height() or _TABLE_HEADER_H
    content_h = hdr_h + table.rowCount() * row_h + 2  # +2 for frame border
    new_h     = max(_TABLE_MIN_HEIGHT, min(content_h, max_h))
    table.setFixedHeight(new_h)


def apply_table_style(table: QTableWidget,
                      max_height: int = _TABLE_MAX_HEIGHT) -> None:
    table.setAlternatingRowColors(True)
    table.verticalHeader().setDefaultSectionSize(_active.table_row_height)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setMinimumSectionSize(90)
    table.setItemDelegate(ElidingDelegate(table))
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # Wire model signals so height auto-adjusts whenever rows change.
    # QTimer.singleShot(0) defers the resize past the current event so the
    # header has been laid out and sizeHint() returns a meaningful value.
    def _resize(*_):
        QTimer.singleShot(0, lambda: _fit_table_height(table, max_height))

    m = table.model()
    m.rowsInserted.connect(_resize)
    m.rowsRemoved.connect(_resize)
    m.modelReset.connect(_resize)

    # Initial size (deferred so the widget has been polished first)
    QTimer.singleShot(0, lambda: _fit_table_height(table, max_height))


def make_empty_label(message: str) -> QLabel:
    lbl = QLabel(message)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setMinimumHeight(80)
    font = QFont(_active.font_family, _active.size_normal)
    font.setItalic(True)
    lbl.setFont(font)
    lbl.setStyleSheet(
        f"color: {_active.text_secondary}; font-style: italic; background: transparent;")
    return lbl


def make_card_shadow() -> QGraphicsDropShadowEffect:
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(_active.shadow_blur)
    shadow.setOffset(QPointF(0, _active.shadow_offset_y))
    shadow.setColor(QColor(0, 0, 0, 20))
    return shadow


def color_for_value(value: float) -> str:
    if value > 0:
        return _active.success
    if value < 0:
        return _active.error
    return _active.text_primary


def make_section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"font-size: {_active.size_small}pt;"
        f" font-weight: bold;"
        f" color: {_active.text_secondary};"
        f" letter-spacing: 1px;"
        f" background: transparent;"
        f" padding: 0;"
        f" margin: 0;")
    return lbl


def make_page_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {_active.size_page_title}pt;"
        f" font-weight: bold;"
        f" color: {_active.text_primary};"
        f" background: transparent;")
    return lbl


def card_frame_style() -> str:
    t = _active
    return (f"background-color: {t.surface};"
            f" border: 1px solid {t.border};"
            f" border-radius: {t.card_border_radius}px;")
