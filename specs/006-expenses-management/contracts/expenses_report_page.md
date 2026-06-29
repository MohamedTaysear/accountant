# Contract: ExpensesReportPage

**Layer**: UI
**File**: `accounting_system/ui/expenses_report_page.py`
**Class**: `ExpensesReportPage(QWidget)`
**Imports**: `logic.expenses_logic`, `expenses_db` (for direct read-only queries if needed)

---

## Layout

```
[Date Range: v] [From: date] [To: date] [Apply]   [Category: v]   [Search: ___]
[Total Expenses: 0.00]
[------------------------------------------------------------------]
| Expense # | Date & Time | Category | Description | Amount | Notes |
|-----------|-------------|----------|-------------|--------|-------|
| ...       |             |          |             |        |       |
[Export to CSV]
```

---

## Controls

### Date Filter (same as ReportsPage)

- `QComboBox` with presets: "Today", "Yesterday", "This Week", "This Month", "Custom Range".
- `QDateEdit` From / To: enabled only for "Custom Range". Calendar popup.
- Apply button: enabled only for "Custom Range". Non-custom presets trigger filter immediately on selection change.

### Category Filter

- `QComboBox` with "All Categories" as first item, then all distinct categories from `expenses_db.get_distinct_categories()`.
- Reloaded each time the page is shown (`showEvent`).
- Selection change triggers filter.

### Search Box

- `QLineEdit`, placeholder "Search…".
- `textChanged` triggers filter (live).

---

## Table

- `QTableWidget`, 6 columns: Expense #, Date & Time, Category, Description, Amount, Notes.
- `NoEditTriggers`, `SelectRows`.
- `horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)`.
- Double-click on a row opens `ExpenseDetailDialog(expense_id, parent=self)`.
- Row's `id` stored in column-0 item's `Qt.UserRole`.

---

## Summary Bar

- Single `QLabel`: "Total Expenses: {sum:,.2f}" — computed as sum of `amount` from current results.

---

## Data Loading

`_apply_filter()`:
1. Compute `start_date`, `end_date` from date filter.
2. Get `category` from category combo (None if "All Categories").
3. Get `search` from search box (None if empty).
4. Call `logic.expenses_logic.get_expenses_for_report(start_date, end_date, category, search)`.
5. Populate table; update total label.

---

## CSV Export

- Button "Export to CSV".
- `QApplication.setOverrideCursor(Qt.WaitCursor)` → `QFileDialog.getSaveFileName` → write headers + rows from current table → restore cursor → success message.
- Columns in CSV: Expense #, Date & Time, Category, Description, Amount, Notes (matching table column order).
- On error: restore cursor, `QMessageBox.critical`.

---

## showEvent

Reloads category combo and applies current filter.

---

# Contract: ExpenseDetailDialog

**File**: `accounting_system/ui/expense_detail_dialog.py`
**Class**: `ExpenseDetailDialog(QDialog)`

Read-only dialog displaying all fields of a single expense.

### Fields Displayed

| Label | Value |
|-------|-------|
| Expense Number | `expense_number` |
| Date & Time | `expense_datetime` |
| Category | `category` |
| Description | `description` |
| Amount | `f"{amount:,.2f}"` |
| Notes | `notes` |
| Created At | `created_at` |

### Construction

`ExpenseDetailDialog(expense_id: int, parent=None)` — loads data via `expenses_db.get_expense_by_id(expense_id)` at init.

Single "Close" button. No editing controls.
