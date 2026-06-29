# Contract: Screen Styling — How Each File Applies the Theme

## Principle

Every UI file MUST depend only on the `theme` module's public API functions. No UI file may reference `LightTheme`, `ThemeDefinition`, `theme._active`, or any token attribute directly. Color values, font sizes, spacing values, and QSS strings are internal to `theme.py`.

**The four calls screens use**:

```python
import theme

theme.apply_table_style(my_table)         # once per table widget
theme.make_empty_label("No records yet.") # once per table empty state
theme.make_card_shadow()                  # once per KPI card
theme.color_for_value(profit_value)       # once per monetary value label
```

Any visual property a screen needs that is NOT covered by these four calls belongs in `build_app_stylesheet()`, not in the screen file. If a screen finds itself needing a raw color hex, that is a signal to add a helper function to `theme.py` instead.

---

## main.py

```python
from ui import theme
from ui.theme import LightTheme   # ← ONLY this file imports the concrete class

theme.set_theme(LightTheme())
app.setFont(QFont(theme._active.font_family, theme._active.size_normal))
# ↑ exception: main.py sets the app font once; this is the only allowed direct token access
app.setStyleSheet(theme.build_app_stylesheet())
```

Applied once before the login window is shown. No other file calls `setStyleSheet()` at the application level. No other file imports `LightTheme` or any `ThemeDefinition` subclass.

---

## ui/main_window.py (Sidebar)

**Required changes**:
- Sidebar widget background and nav button styles come from the global QSS (no per-widget `setStyleSheet`).
- Nav buttons include icons loaded from `ui/icons/<page>.svg` via `QIcon(path)`.
- Active nav button: set `btn.setProperty("class", "nav-active")` + `btn.style().unpolish(btn); btn.style().polish(btn)` to trigger QSS property selector.
- Sidebar width: unchanged (180px per existing code).
- No direct color hex values in this file.

---

## ui/login_window.py

**Required changes**:
- Login button: `btn.setProperty("class", "primary")`.
- Error label color: add a `theme.make_error_label(text)` helper to `theme.py` and call it, OR inline the error label using the global QSS `QLabel[class="error"]` selector. Do not hardcode `#DC2626` in the screen file.
- All other styling comes from the global QSS.

---

## ui/dashboard_page.py (KPI Cards)

**Required changes**:
- Each KPI card: `card_widget.setGraphicsEffect(theme.make_card_shadow())`.
- Card layout margins: set by the card's inner `QVBoxLayout`/`QHBoxLayout` — margins come from the global QSS `QWidget` padding rules, or if explicit: use a layout call that does NOT hardcode a numeric constant from `theme.py` directly (wrap in a helper if needed).
- Value labels for profit/loss metrics: `label.setStyleSheet(f"color: {theme.color_for_value(value)}; font-weight: bold;")`.
- Value labels for neutral metrics (stock count, product count): no stylesheet override needed — global QSS handles `QLabel`.
- Low Stock table: `theme.apply_table_style(table)` + `theme.make_empty_label("No products are currently low on stock.")`.
- No raw hex color strings in this file.

---

## ui/products_page.py

**Required changes**:
- Products table: `theme.apply_table_style(table)`.
- Empty state (no data): `theme.make_empty_label("No products added yet.")` — shown when table has 0 rows.
- Empty state (search empty): `theme.make_empty_label("No results match your search.")` — shown when search returns 0 rows.
- Add/Edit buttons: `btn.setProperty("class", "primary")`.
- Delete/Deactivate buttons: `btn.setProperty("class", "destructive")`.
- Each `QTableWidgetItem` with text content: `item.setToolTip(full_value)`.
- No raw hex color strings in this file.

---

## ui/product_dialog.py

**Required changes**:
- Dialog background and input styling come from global QSS.
- Save button: `btn.setProperty("class", "primary")`.
- Cancel button: no property (default/neutral style from global QSS).
- No raw hex color strings in this file.

---

## ui/purchases_page.py

**Required changes**:
- Line-items table: `theme.apply_table_style(table)`.
- Empty state: `theme.make_empty_label("No items added to this invoice yet.")`.
- Save Invoice button: `btn.setProperty("class", "primary")`.
- Clear Invoice button: `btn.setProperty("class", "destructive")`.
- Add to Invoice button: `btn.setProperty("class", "primary")`.
- Each text `QTableWidgetItem`: `item.setToolTip(full_value)`.
- No raw hex color strings in this file.

---

## ui/sales_page.py

Same pattern as `purchases_page.py`. Empty state message: `"No items added to this invoice yet."`.

---

## ui/expenses_page.py

Same pattern as `purchases_page.py`. Empty state message: `"No expense lines added to this invoice yet."`.

---

## ui/reports_page.py

**Required changes**:
- Sales, Purchases, and Expenses history tables: `theme.apply_table_style(table)` for each.
- Empty states (no data and search-empty) for each table section.
- Profit/loss summary values: `label.setStyleSheet(f"color: {theme.color_for_value(net_value)};")`.
- Export CSV button: default/neutral style (no property override needed).
- No raw hex color strings in this file.

---

## ui/invoice_detail_dialog.py

**Required changes**:
- Line-items table: `theme.apply_table_style(table)`.
- Total/net value labels: `label.setStyleSheet(f"color: {theme.color_for_value(net_value)};")`.
- Void button: `btn.setProperty("class", "destructive")`.
- Close/Print buttons: default/neutral style.
- No raw hex color strings in this file.

---

## ui/expense_detail_dialog.py

**Required changes**:
- Items table: `theme.apply_table_style(table)`.
- Close button: default/neutral style.
- No raw hex color strings in this file.

---

## ui/change_password_dialog.py

**Required changes**:
- Save button: `btn.setProperty("class", "primary")`.
- Cancel button: default/neutral style.
- Error label (mismatched passwords): use `theme.make_error_label(text)` helper — do not hardcode a color.
- No raw hex color strings in this file.

---

## Tooltip Rule (applies to ALL tables)

Wherever a `QTableWidgetItem` is created with text content, set the full value as its tooltip:

```python
item = QTableWidgetItem(display_text)
item.setToolTip(full_value)
table.setItem(row, col, item)
```

---

## Button Class Convention

```python
btn.setProperty("class", "primary")      # primary action
btn.setProperty("class", "destructive")  # destructive action
# default (no property) = secondary/neutral
btn.style().unpolish(btn)
btn.style().polish(btn)   # required after setting property on a live widget
```

---

## Theme-Expansion Guarantee (FR-019 / SC-010)

If a Dark theme is added in a future phase:

```python
# main.py only:
from ui.theme import DarkTheme
theme.set_theme(DarkTheme())
app.setFont(QFont(theme._active.font_family, theme._active.size_normal))
app.setStyleSheet(theme.build_app_stylesheet())
```

**Zero changes are required in any screen or dialog file.** This guarantee is only maintained if screens never access `theme._active` directly, never import `LightTheme`, and never embed raw hex color strings.
