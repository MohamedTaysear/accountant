# Contract: ui/theme.py

## Purpose

Central design system module. The single source of truth for all visual styling. Structured to support multiple themes without requiring changes to individual screen files. Every UI file calls only the module-level helper functions — never the internal theme class or its token attributes.

## Module Location

`accounting_system/ui/theme.py`

## Imports Allowed

- `PySide6.QtWidgets` (QLabel, QGraphicsDropShadowEffect, QStyledItemDelegate, QTableWidget, QAbstractItemView)
- `PySide6.QtCore` (Qt, QPointF)
- `PySide6.QtGui` (QPainter, QFont, QColor)
- No imports from `logic/`, `*_db.py`, or `database.py` — UI layer only.

---

## Class: `ThemeDefinition`

Base class that defines the full design token vocabulary. All tokens are instance attributes. Subclasses override only the tokens they change. Screens are never coupled to this class — they use only module-level functions.

### Color tokens

```python
primary          = ""   # Primary action color
primary_dark     = ""   # Primary hover/pressed state
success          = ""   # Profit values, positive indicators
success_light    = ""   # Success card background
warning          = ""   # Low-stock and caution indicators
warning_light    = ""   # Warning card background
error            = ""   # Negative values, destructive actions, error states
error_light      = ""   # Error card background
background       = ""   # Application window background
surface          = ""   # Cards, dialogs, table backgrounds
surface_alt      = ""   # Alternating table row background
border           = ""   # Table grid, card borders, input borders
border_focus     = ""   # Focused input highlight ring
text_primary     = ""   # Main body text
text_secondary   = ""   # Labels, captions, secondary info
text_disabled    = ""   # Disabled control text
nav_bg           = ""   # Sidebar navigation background
nav_text         = ""   # Sidebar item text
nav_active       = ""   # Active navigation item highlight
```

### Typography tokens

```python
font_family      = ""   # Font family string
size_normal      = 0    # Normal body text (pt)
size_small       = 0    # Caption/secondary label (pt)
size_section     = 0    # Group box / section title (pt)
size_kpi_value   = 0    # Dashboard KPI number (pt)
size_kpi_label   = 0    # Dashboard KPI label (pt)
size_heading     = 0    # Page-level heading (pt)
```

### Spacing tokens

```python
spacing_xs = 0   # 4px — tight inner padding
spacing_sm = 0   # 8px — form rows, button padding
spacing_md = 0   # 12px — card padding, table cell padding
spacing_lg = 0   # 16px — card horizontal padding, form margins
spacing_xl = 0   # 24px — section separators, major gaps
```

### Component constants

```python
card_border_radius   = 0   # All KPI card corners (px)
input_border_radius  = 0   # All input field corners (px)
button_border_radius = 0   # All button corners (px)
table_row_height     = 0   # All table row heights (px)
shadow_blur          = 0   # Card drop shadow blur (px)
shadow_offset_y      = 0   # Card drop shadow vertical offset (px)
nav_active_bar_width = 0   # Active nav item left accent (px)
```

---

## Class: `LightTheme(ThemeDefinition)`

Provides all concrete values for the Light theme (the only theme implemented in this phase). Every token is set to a non-empty value.

```python
primary          = "#2563EB"
primary_dark     = "#1D4ED8"
success          = "#16A34A"
success_light    = "#DCFCE7"
warning          = "#D97706"
warning_light    = "#FEF3C7"
error            = "#DC2626"
error_light      = "#FEE2E2"
background       = "#F1F5F9"
surface          = "#FFFFFF"
surface_alt      = "#F8FAFC"
border           = "#E2E8F0"
border_focus     = "#93C5FD"
text_primary     = "#1E293B"
text_secondary   = "#64748B"
text_disabled    = "#CBD5E1"
nav_bg           = "#1E293B"
nav_text         = "#CBD5E1"
nav_active       = "#2563EB"

font_family      = "Segoe UI"
size_normal      = 9
size_small       = 8
size_section     = 10
size_kpi_value   = 18
size_kpi_label   = 8
size_heading     = 11

spacing_xs = 4
spacing_sm = 8
spacing_md = 12
spacing_lg = 16
spacing_xl = 24

card_border_radius   = 6
input_border_radius  = 4
button_border_radius = 4
table_row_height     = 28
shadow_blur          = 8
shadow_offset_y      = 2
nav_active_bar_width = 3
```

---

## Module-Level State

```python
_active: ThemeDefinition = LightTheme()
```

Private. Not accessed by screen files. All public functions read from `_active`.

---

## Function: `set_theme(t: ThemeDefinition) -> None`

Replaces the active theme. Called once at startup; in future may be called when the user switches themes.

```python
def set_theme(t: ThemeDefinition) -> None:
    global _active
    _active = t
```

---

## Function: `build_app_stylesheet() -> str`

Builds and returns the global QSS string from the active theme. Applied via `QApplication.setStyleSheet()` in `main.py`.

**Coverage** (all these widget types MUST be styled):

| Widget Type | Required Properties |
|---|---|
| `QWidget` | `background-color: {t.background}; font-family: {t.font_family}; font-size: {t.size_normal}pt` |
| `QPushButton` (default) | `background-color: {t.surface}; border: 1px solid {t.border}; border-radius: {t.button_border_radius}px; padding; color: {t.text_primary}` |
| `QPushButton[class="primary"]` | `background-color: {t.primary}; color: white; border: none; hover: {t.primary_dark}` |
| `QPushButton[class="destructive"]` | `background-color: {t.error}; color: white; border: none` |
| `QPushButton:disabled` | `color: {t.text_disabled}; background-color: {t.surface_alt}` |
| `QLineEdit` | `border: 1px solid {t.border}; border-radius: {t.input_border_radius}px; padding: {t.spacing_sm}px; background: {t.surface}` |
| `QLineEdit:focus` | `border-color: {t.border_focus}` |
| `QComboBox` | same as QLineEdit |
| `QComboBox:focus` | `border-color: {t.border_focus}` |
| `QDateTimeEdit` | same as QLineEdit |
| `QSpinBox` | same as QLineEdit |
| `QDoubleSpinBox` | same as QLineEdit |
| `QGroupBox` | `border: 1px solid {t.border}; border-radius: 4px; title color: {t.text_primary}; bold` |
| `QDialog` | `background-color: {t.surface}` |
| `QScrollBar:vertical` | thin, styled with `{t.border_focus}` thumb |
| `QTableWidget` | `gridline-color: {t.border}; background: {t.surface}` |
| `QHeaderView::section` | `background: {t.background}; border-bottom: 2px solid {t.border}; font-weight: bold` |
| `QTableWidget::item` | `padding: {t.spacing_md}px; color: {t.text_primary}` |
| `QTableWidget::item:selected` | `background: {t.primary} at ~15% opacity; color: {t.text_primary}` |
| `QTableWidget::item:alternate` | `background: {t.surface_alt}` |

**MUST NOT** use `#objectName` selectors.

**MUST NOT** call `QApplication.instance()` or produce side effects — returns a string only.

---

## Function: `apply_table_style(table: QTableWidget) -> None`

Configures a QTableWidget with all standard visual rules. Called once per table after construction.

**Required effects**:
- `table.setAlternatingRowColors(True)`
- `table.verticalHeader().setDefaultSectionSize(_active.table_row_height)`
- `table.verticalHeader().setVisible(False)`
- `table.setShowGrid(True)`
- `table.setSelectionBehavior(QAbstractItemView.SelectRows)`
- `table.setEditTriggers(QAbstractItemView.NoEditTriggers)`
- `table.horizontalHeader().setHighlightSections(False)`
- `table.setItemDelegate(ElidingDelegate(table))`

---

## Function: `make_empty_label(message: str) -> QLabel`

Returns a `QLabel` for displaying as an empty-state overlay.

**Required properties**:
- `setAlignment(Qt.AlignCenter)`
- Font: italic, `_active.size_normal` pt
- Color: `_active.text_secondary` (via `setStyleSheet("color: ...")`)
- Text: `message` parameter

**Callers MUST**:
- Show the label and hide the table when row count is 0.
- Hide the label and show the table when row count > 0.
- Pass `"No [entity] added yet."` for empty-data state.
- Pass `"No results match your search."` for empty-search state.

---

## Function: `make_card_shadow() -> QGraphicsDropShadowEffect`

Returns a pre-configured drop shadow for KPI cards.

**Required properties**:
- `blurRadius`: `_active.shadow_blur`
- `offset`: `QPointF(0, _active.shadow_offset_y)`
- `color`: `QColor(0, 0, 0, 26)` (≈10% black opacity, theme-invariant)

---

## Function: `color_for_value(value: float) -> str`

Returns a hex color string from the active theme:
- `value > 0` → `_active.success`
- `value < 0` → `_active.error`
- `value == 0` → `_active.text_primary`

---

## Class: `ElidingDelegate(QStyledItemDelegate)`

Renders cell text with `Qt.ElideRight` when text overflows the column width.

**Required behavior**:
- Override `paint(painter, option, index)`.
- Compute `elidedText = option.fontMetrics.elidedText(text, Qt.ElideRight, option.rect.width() - 2 * _active.spacing_md)`.
- Draw with `painter.drawText(option.rect, Qt.AlignVCenter | Qt.AlignLeft, elidedText)`.
- Does NOT set tooltips — the data-populating code sets `QTableWidgetItem.setToolTip(full_value)`.

---

## Constraints

- `theme.py` MUST NOT import from `logic/`, `*_db.py`, or `database.py`.
- Screen files MUST NOT import `ThemeDefinition`, `LightTheme`, or access `_active` directly.
- `build_app_stylesheet()` MUST be a pure function (returns string, no side effects).
- `apply_table_style()` is the only exported function with widget side effects.
- Adding a new theme in the future MUST NOT require modifying any screen or dialog file.
