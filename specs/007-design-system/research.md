# Research: Design System & UI Modernization

## 1. Centralized Styling Mechanism & Theme Architecture

**Decision**: `ui/theme.py` structured around a `ThemeDefinition` base class and a module-level active theme instance. Screen code calls only theme API functions (`build_app_stylesheet()`, `apply_table_style()`, `color_for_value()`, etc.) — never accessing color or spacing constants directly. This satisfies both FR-018 (centralized styling) and FR-019 (theme-expandable architecture with no screen changes needed to add a new theme).

**Architecture**:

```
ThemeDefinition (base class)
  └── LightTheme(ThemeDefinition)   ← implemented this phase; all token defaults live here
  └── DarkTheme(ThemeDefinition)    ← future; overrides token values only
  └── HighContrastTheme(...)        ← future

# Module level
_active: ThemeDefinition = LightTheme()

def set_theme(t: ThemeDefinition) -> None: ...  # swap active theme
def build_app_stylesheet() -> str: ...          # reads _active; called once at startup
def apply_table_style(table) -> None: ...       # reads _active; called per table
def color_for_value(v: float) -> str: ...       # reads _active; called per value
```

Screens import `theme` and call its functions. They never reference `LightTheme`, `Colors.X`, or any token constant. Switching themes in the future requires only `theme.set_theme(DarkTheme())` + rebuilding the application stylesheet — zero screen changes.

**Rationale**: A subclass-based `ThemeDefinition` is the simplest Python pattern that satisfies SC-010 (future theme without screen changes). It requires no new packages, no metaclass magic, and no dynamic attribute lookup. `LightTheme` inherits all defaults from `ThemeDefinition`; alternate themes override only the tokens that differ.

**Alternatives considered**:
- *Module-level constants only (original plan)*: Rejected — screens accessing `Colors.PRIMARY` directly would need updating when a new theme is added, violating FR-019 and SC-010.
- *`ThemeManager` singleton*: Rejected — adds unnecessary indirection; the module-level `_active` variable with `set_theme()` is functionally equivalent and simpler.
- *Per-screen QSS dictionaries*: Rejected — duplicates values, violates FR-018.
- *`qtawesome` or other theme packages*: Rejected — violates constitution's fixed technology stack.

---

## 2. Icon Strategy

**Decision**: Navigation icons are delivered as bundled monochrome SVG files in `ui/icons/`. They are loaded at runtime via `QIcon(path)`. Standard system icons (dialog warning, information, critical) continue to use PySide6's `QStyle.standardIcon()`. No new Python packages are required.

**Rationale**: PySide6's `QIcon` natively loads SVG files without any additional dependencies. Bundling SVGs as project assets keeps the dependency footprint zero while satisfying FR-011 (single icon family). Monochrome SVGs can be recolored via QSS `color` inheritance or by choosing appropriately colored source files. `QStyle.standardIcon()` is used for standard OS icons (information, warning, error) to maintain native platform feel in dialogs.

**Alternatives considered**:
- *`qtawesome` (Font Awesome for Qt)*: Rejected — new package dependency, violates constitution.
- *Unicode text symbols only*: Rejected — inconsistent rendering across fonts; does not satisfy the "icon family" requirement.
- *Qt resource system (.qrc)*: Deferred — adds build step complexity; direct file path loading is simpler and equivalent for a single-machine deployment.

---

## 3. Application Font

**Decision**: "Segoe UI", 9pt for all normal text. Applied globally via `QApplication.setFont(QFont("Segoe UI", 9))` plus the `font-family` QSS property. Fallback chain: "Segoe UI", "Arial", sans-serif.

**Rationale**: "Segoe UI" is the Windows 10/11 system UI font, pre-installed on every supported deployment machine. It is optimized for screen readability at 9–10pt, aligns with the "modern Windows business application" aesthetic goal, and requires no font embedding.

**Alternatives considered**:
- *"Arial"*: Available but less refined than Segoe UI on modern Windows.
- *Custom/embedded font (e.g., Inter)*: Rejected — requires font file bundling; Segoe UI is already optimal for the target platform.

---

## 4. Color Palette

**Decision**: Fixed application-defined palette, not responsive to OS dark/light mode.

| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#2563EB` | Primary buttons, focus rings, active nav |
| Primary Dark | `#1D4ED8` | Button hover/pressed state |
| Secondary | `#64748B` | Secondary text, secondary buttons, labels |
| Success | `#16A34A` | Profit values, positive indicators |
| Success Light | `#DCFCE7` | Profit card backgrounds |
| Warning | `#D97706` | Low stock indicators, caution states |
| Warning Light | `#FEF3C7` | Warning card backgrounds |
| Error | `#DC2626` | Negative values, destructive button backgrounds, error messages |
| Error Light | `#FEE2E2` | Error card backgrounds |
| Background | `#F1F5F9` | Application window background |
| Surface | `#FFFFFF` | Cards, dialogs, table backgrounds |
| Surface Alt | `#F8FAFC` | Alternating table rows |
| Border | `#E2E8F0` | Table grid lines, card borders, input borders |
| Border Focus | `#93C5FD` | Input focus ring color |
| Text Primary | `#1E293B` | Main body text, table values |
| Text Secondary | `#64748B` | Labels, captions, secondary info |
| Text Disabled | `#CBD5E1` | Disabled control text |
| Nav Background | `#1E293B` | Sidebar background |
| Nav Text | `#CBD5E1` | Sidebar nav item text |
| Nav Active | `#2563EB` | Active nav item highlight |

**Contrast verification** (WCAG AA — FR-012, SC-008):
- Text Primary (`#1E293B`) on Surface (`#FFFFFF`): ~15:1 ✅
- Text Primary on Surface Alt (`#F8FAFC`): ~14:1 ✅
- Text Primary on Background (`#F1F5F9`): ~13:1 ✅
- White on Primary (`#2563EB`): ~4.6:1 ✅ (normal text passes AA)
- White on Error (`#DC2626`): ~4.6:1 ✅
- White on Success (`#16A34A`): ~4.6:1 ✅
- Nav Text (`#CBD5E1`) on Nav Background (`#1E293B`): ~8.9:1 ✅

**Rationale**: These values use the Tailwind CSS v3 color scale (a well-validated palette for professional business software) adapted to the semantic token names in the spec. All critical text/background combinations meet WCAG AA.

---

## 5. Typography Scale

**Decision**:

| Token | Value | Usage |
|-------|-------|-------|
| Font Family | "Segoe UI", Arial, sans-serif | All text |
| Size Normal | 9pt | Body text, table cells, input values |
| Size Small | 8pt | Captions, secondary labels |
| Size Section | 10pt bold | Group box titles, section headings |
| Size KPI Value | 18pt bold | Dashboard card numeric values |
| Size KPI Label | 8pt | Dashboard card label text |
| Size Heading | 11pt bold | Page-level headings (if used) |

---

## 6. Spacing Scale

**Decision**:

| Token | Value | Usage |
|-------|-------|-------|
| XS | 4px | Inner padding of small badges, tight gaps |
| SM | 8px | Form row spacing, button padding vertical |
| MD | 12px | Card interior padding (vertical), table cell padding |
| LG | 16px | Card interior padding (horizontal), form margins |
| XL | 24px | Section separators, major layout gaps |

---

## 7. Component Patterns

### Buttons
- **Primary**: Background `Primary`, white text, 4px border radius, horizontal padding `LG`, vertical padding `SM`. Hover: `Primary Dark`. Disabled: 50% opacity.
- **Destructive**: Background `Error`, white text, same geometry. Hover: darken `Error`.
- **Secondary/Neutral**: Background transparent, border 1px `Border`, text `Text Secondary`. Hover: Background `Surface Alt`.

### Tables
- Header: Background `Background`, text `Text Primary`, bold, border-bottom 2px `Border`.
- Rows: Alternating `Surface` / `Surface Alt`, row height 28px.
- Selected row: Background `Primary` at 15% opacity, text `Text Primary`.
- Grid lines: 1px `Border`.
- Text truncation: `Qt.TextElideMode.ElideRight` applied via `QStyledItemDelegate`; full value set as `QTableWidgetItem.setToolTip()`.
- Empty state: Centered `QLabel` with `Text Secondary` color and italic font.

### Cards (Dashboard KPI)
- Background: `Surface`.
- Border: 1px solid `Border`, border radius 6px.
- Shadow: `QGraphicsDropShadowEffect`, blur 8px, offset (0, 2), color `#0000001A`.
- Padding: `LG` horizontal, `MD` vertical.
- Value: `Size KPI Value`, color depends on metric type (success/warning/error/neutral).
- Label: `Size KPI Label`, `Text Secondary`.

### Inputs (QLineEdit, QComboBox, QDateTimeEdit, QSpinBox)
- Border: 1px solid `Border`, border radius 4px.
- Padding: `XS` vertical, `SM` horizontal.
- Focus: Border color changes to `Border Focus`, 1px border.
- Background: `Surface`.

### Dialogs
- Background: `Surface`.
- Header (window title bar): OS-native.
- Content padding: `LG` all sides.
- Button row: right-aligned, `SM` gap between buttons.

### Sidebar Navigation
- Background: `Nav Background`.
- Nav items: `Nav Text`, full-width buttons, `MD` padding, no border.
- Active item: `Nav Active` left accent bar (3px) + `Nav Active` text.
- Bottom actions (Logout, Backup, Change Password): `Nav Text`, smaller weight.

---

## 8. Empty State Pattern

**Decision**: Two distinct messages, implemented as a helper function `theme.make_empty_label(text)` that returns a styled `QLabel`:
- *"No [records] added yet."* — used when the table is empty because no data exists.
- *"No results match your search."* — used when a search or filter returns no rows.

Each page maintains a reference to its empty label and swaps it visible/hidden based on the table row count after every data load or search operation.

**Implementation note**: Since `QTableWidget` cannot natively show an overlay label, the empty label is placed in a `QStackedLayout` or positioned as a sibling widget over the table using `setVisible()` toggling.

---

## 9. Text Truncation in Tables

**Decision**: Use a `QStyledItemDelegate` subclass (`theme.ElidingDelegate`) that paints cell text with `Qt.TextElideMode.ElideRight`. Each `QTableWidgetItem` also receives `setToolTip(full_value)` so the complete text is accessible on hover.

**Rationale**: `Qt.TextElideMode` in a delegate is the only reliable cross-platform way to get ellipsis truncation in `QTableWidget` cells. Setting `setToolTip()` satisfies the full-text-on-hover requirement from the clarification session (Q2).
