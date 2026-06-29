# Contract: ExpensesPage

**Layer**: UI
**File**: `accounting_system/ui/expenses_page.py`
**Class**: `ExpensesPage(QWidget)`
**Imports**: `logic.expenses_logic` only (no direct `expenses_db`, no `database`)

---

## Layout

```
[Search: _______________] [Add Expense]
[------------------------------------------]
| Expense # | Date & Time | Category | Description | Amount | Notes | Actions |
|-----------|-------------|----------|-------------|--------|-------|---------|
| ...       | ...         | ...      | ...         | ...    | ...   | [Edit] [Delete] |
```

- Search box: `QLineEdit`, placeholder "Search expenses…". Connected to `textChanged` → live filter via `logic.expenses_logic.get_expenses(search)`.
- Add Expense button: opens `ExpenseDialog(parent=self)` in add mode. On `Accepted`, reloads table.
- Table: `QTableWidget`, 7 columns, `NoEditTriggers`, `SelectRows`. Column widths: Expense # (stretch), Date & Time (fixed ~150px), Category (stretch), Description (stretch), Amount (fixed ~100px), Notes (stretch), Actions (fixed ~140px).
- Actions column: each row contains a `QWidget` with two buttons — "Edit" and "Delete" — laid out `QHBoxLayout`.

---

## Table Loading

`_load_expenses(search="")`:
1. Call `logic.expenses_logic.get_expenses(search or None)`.
2. Clear table, set row count, populate cells.
3. Amount formatted as `f"{row['amount']:,.2f}"`.
4. Date & Time displayed as stored (full `YYYY-MM-DD HH:MM:SS`).
5. Actions cell: create widget with Edit and Delete buttons; store `row['id']` in button's `setProperty('expense_id', ...)`.

---

## Edit Action

Opens `ExpenseDialog(expense_id=row_id, parent=self)`. On `Accepted`, reloads table.

---

## Delete Action

1. Show `QMessageBox.question` confirmation.
2. On Yes: `QApplication.setOverrideCursor(Qt.WaitCursor)`.
3. Call `logic.expenses_logic.delete_expense(expense_id)`.
4. `QApplication.restoreOverrideCursor()`.
5. Reload table.
6. On exception: restore cursor, show `QMessageBox.critical`.

---

## Refresh

`showEvent` calls `_load_expenses()` to ensure data is current when the page becomes visible.

---

# Contract: ExpenseDialog

**File**: `accounting_system/ui/expense_dialog.py`
**Class**: `ExpenseDialog(QDialog)`
**Modes**: Add (`expense_id=None`) and Edit (`expense_id=int`)

### Fields

| Widget | Field | Default (Add) | Editable |
|--------|-------|---------------|----------|
| `QDateTimeEdit` | expense_datetime | `database.now_cairo()` parsed | Yes |
| `QComboBox` (editable) | category | "" | Yes |
| `QLineEdit` | description | "" | Yes |
| `QDoubleSpinBox` | amount | 0.01, min=0.01, decimals=2, max=9999999.99 | Yes |
| `QLineEdit` | notes | "" | Yes |

### Category Combo Box

- Populated via `logic.expenses_logic.get_categories()` on dialog open.
- `setEditable(True)`.
- `QCompleter` with `Qt.CaseInsensitive` match mode attached.

### Edit Mode Pre-population

Load expense by id via `expenses_db.get_expense_by_id()` (or pass data dict from caller). Pre-fill all fields.

### Save Logic

1. Read field values.
2. Call `logic.expenses_logic.add_expense(...)` or `update_expense(...)`.
3. On `ValueError`: show `QMessageBox.warning` with error text; do not close dialog.
4. On success: `QApplication.setOverrideCursor(Qt.WaitCursor)` → call logic → restore cursor → `self.accept()`.
5. On unexpected exception: restore cursor, show `QMessageBox.critical`.
