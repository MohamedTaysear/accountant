# Data Model: Design System & UI Modernization

> This phase introduces no database schema changes. The "data model" for this feature is the **design token structure** — the public API of `ui/theme.py` that all screens and dialogs consume.

---

## Theme Class Hierarchy

The design system is organized around a `ThemeDefinition` base class. All design tokens (colors, typography, spacing, component constants) are attributes of this class. `LightTheme` subclasses it for this phase, providing all concrete values. Future themes (Dark, High Contrast) subclass it and override only the tokens that differ.

```
ThemeDefinition          ← abstract base; defines the full token vocabulary
  └── LightTheme         ← this phase; all token defaults live here
  └── DarkTheme          ← future; overrides subset of tokens
  └── HighContrastTheme  ← future; overrides subset of tokens
```

A module-level `_active: ThemeDefinition` variable holds the current theme. All public theme functions read from `_active`. Screens never access `_active` directly — they call only the module-level helper functions.

---

## ThemeDefinition Token Vocabulary

All tokens are instance attributes with default values on `ThemeDefinition`. `LightTheme` overrides all of them with the concrete Light theme values. Future themes override only what they change.

### Color Tokens

| Token | Type | Semantic Purpose |
|---|---|---|
| `primary` | `str` (hex) | Primary action color |
| `primary_dark` | `str` (hex) | Primary hover/pressed state |
| `success` | `str` (hex) | Profit values, positive indicators |
| `success_light` | `str` (hex) | Profit card background |
| `warning` | `str` (hex) | Low-stock and caution indicators |
| `warning_light` | `str` (hex) | Warning card background |
| `error` | `str` (hex) | Negative values, destructive actions, error states |
| `error_light` | `str` (hex) | Error card background |
| `background` | `str` (hex) | Application window background |
| `surface` | `str` (hex) | Cards, dialogs, table backgrounds |
| `surface_alt` | `str` (hex) | Alternating table row background |
| `border` | `str` (hex) | Table grid lines, card borders, input borders |
| `border_focus` | `str` (hex) | Focused input highlight ring |
| `text_primary` | `str` (hex) | Main body text |
| `text_secondary` | `str` (hex) | Labels, captions, secondary info |
| `text_disabled` | `str` (hex) | Disabled control text |
| `nav_bg` | `str` (hex) | Sidebar navigation background |
| `nav_text` | `str` (hex) | Sidebar item text |
| `nav_active` | `str` (hex) | Active navigation item highlight |

### Typography Tokens

| Token | Type | Description |
|---|---|---|
| `font_family` | `str` | Font family string for QFont and QSS |
| `size_normal` | `int` | Normal body text size (pt) |
| `size_small` | `int` | Caption/secondary label size (pt) |
| `size_section` | `int` | Group box / section title size (pt) |
| `size_kpi_value` | `int` | Dashboard KPI number size (pt) |
| `size_kpi_label` | `int` | Dashboard KPI label size (pt) |
| `size_heading` | `int` | Page-level heading size (pt) |

### Spacing Tokens

| Token | Type | Description |
|---|---|---|
| `spacing_xs` | `int` | 4px — tight inner padding |
| `spacing_sm` | `int` | 8px — form rows, button vertical padding |
| `spacing_md` | `int` | 12px — card vertical padding, table cell padding |
| `spacing_lg` | `int` | 16px — card horizontal padding, form margins |
| `spacing_xl` | `int` | 24px — section separators, major layout gaps |

### Component Constants

| Token | Type | Description |
|---|---|---|
| `card_border_radius` | `int` | 6px — all KPI card corners |
| `input_border_radius` | `int` | 4px — all input field corners |
| `button_border_radius` | `int` | 4px — all button corners |
| `table_row_height` | `int` | 28px — all table row heights |
| `shadow_blur` | `int` | 8px — card drop shadow blur radius |
| `shadow_offset_y` | `int` | 2px — card drop shadow vertical offset |
| `nav_active_bar_width` | `int` | 3px — active nav item left accent width |

---

## LightTheme Values

`LightTheme` inherits `ThemeDefinition` and sets all tokens to the Light palette:

| Token | Light Value |
|---|---|
| `primary` | `#2563EB` |
| `primary_dark` | `#1D4ED8` |
| `success` | `#16A34A` |
| `success_light` | `#DCFCE7` |
| `warning` | `#D97706` |
| `warning_light` | `#FEF3C7` |
| `error` | `#DC2626` |
| `error_light` | `#FEE2E2` |
| `background` | `#F1F5F9` |
| `surface` | `#FFFFFF` |
| `surface_alt` | `#F8FAFC` |
| `border` | `#E2E8F0` |
| `border_focus` | `#93C5FD` |
| `text_primary` | `#1E293B` |
| `text_secondary` | `#64748B` |
| `text_disabled` | `#CBD5E1` |
| `nav_bg` | `#1E293B` |
| `nav_text` | `#CBD5E1` |
| `nav_active` | `#2563EB` |
| `font_family` | `"Segoe UI"` |
| `size_normal` | `9` |
| `size_small` | `8` |
| `size_section` | `10` |
| `size_kpi_value` | `18` |
| `size_kpi_label` | `8` |
| `size_heading` | `11` |
| `spacing_xs` | `4` |
| `spacing_sm` | `8` |
| `spacing_md` | `12` |
| `spacing_lg` | `16` |
| `spacing_xl` | `24` |
| `card_border_radius` | `6` |
| `input_border_radius` | `4` |
| `button_border_radius` | `4` |
| `table_row_height` | `28` |
| `shadow_blur` | `8` |
| `shadow_offset_y` | `2` |
| `nav_active_bar_width` | `3` |

---

## Module-Level Public API

Screen files call only these module-level functions. They never access the active theme instance or its tokens directly.

| Symbol | Signature | Description |
|---|---|---|
| `set_theme(t)` | `(ThemeDefinition) -> None` | Replaces the active theme. Called once at startup (and in future when user switches themes). |
| `build_app_stylesheet()` | `() -> str` | Builds and returns the global QSS string from the active theme. Applied to `QApplication`. |
| `apply_table_style(table)` | `(QTableWidget) -> None` | Configures all standard table visual rules using the active theme. |
| `make_empty_label(message)` | `(str) -> QLabel` | Returns a styled empty-state label from the active theme. |
| `make_card_shadow()` | `() -> QGraphicsDropShadowEffect` | Returns a drop shadow from the active theme. |
| `color_for_value(value)` | `(float) -> str` | Returns success/error/primary hex from the active theme based on numeric sign. |
| `ElidingDelegate` | `QStyledItemDelegate` subclass | Installed by `apply_table_style()`. Paints text with `ElideRight`. |

---

## Relationships

```
ui/theme.py
  ├── ThemeDefinition (base class, full token vocabulary)
  ├── LightTheme(ThemeDefinition) ← active this phase
  ├── _active: ThemeDefinition = LightTheme()
  │
  └── module-level functions (read _active)
        ├── set_theme()
        ├── build_app_stylesheet()
        ├── apply_table_style()
        ├── make_empty_label()
        ├── make_card_shadow()
        └── color_for_value()

main.py
  └── theme.set_theme(LightTheme())    ← explicit, documents the active theme
  └── app.setStyleSheet(theme.build_app_stylesheet())

Every UI file
  └── import theme
        ├── theme.apply_table_style(table)
        ├── theme.make_empty_label("...")
        ├── theme.make_card_shadow()
        └── theme.color_for_value(value)
        (NO direct access to theme._active, ThemeDefinition, or token attributes)

Future dark mode:
  └── theme.set_theme(DarkTheme())
  └── app.setStyleSheet(theme.build_app_stylesheet())
      ← zero changes to any screen or dialog file
```

---

## Validation Rules

- `build_app_stylesheet()` MUST NOT contain screen-specific `#objectName` selectors.
- `apply_table_style()` MUST install `ElidingDelegate` on all columns; tooltip content is set by the data-populating code.
- `color_for_value()` MUST return only values from the active theme's token attributes.
- Screen files MUST NOT import `LightTheme`, `ThemeDefinition`, or access `theme._active`. They call only the module-level functions above.
- `ThemeDefinition` subclasses MUST NOT import from `logic/`, `*_db.py`, or `database.py`.
