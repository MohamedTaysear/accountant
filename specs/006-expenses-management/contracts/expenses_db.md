# Contract: expenses_db

**Layer**: Data Access
**File**: `accounting_system/expenses_db.py`
**Imports**: `database` only (no PySide6, no logic layer)

---

## Functions

### `insert_expense(expense_datetime, category, description, amount, notes) -> str`

Inserts a new expense inside a single transaction. Returns the generated `expense_number`.

- Insert row with `expense_number='PENDING'` and all supplied fields; `created_at` = `database.now_cairo()`.
- Retrieve `last_insert_rowid()` → `new_id`.
- Compute `expense_number = f"EXP-{new_id:06d}"`.
- Update the row's `expense_number`.
- Commit. Rollback on any exception and re-raise.

---

### `update_expense(expense_id, expense_datetime, category, description, amount, notes) -> None`

Updates all user-editable fields for an existing expense. `created_at` is NOT updated.

---

### `delete_expense(expense_id) -> None`

Hard-deletes the expense row. No soft-delete / voiding.

---

### `get_expense_by_id(expense_id) -> sqlite3.Row | None`

Returns the single row for `id = expense_id`, or `None`.

---

### `get_all_expenses(search=None) -> list[sqlite3.Row]`

Returns all expenses ordered by `expense_datetime DESC, id DESC`.

If `search` is a non-empty string, filters all four text fields with `LIKE '%{search}%' COLLATE NOCASE`.

---

### `get_expenses_for_report(start_date=None, end_date=None, category=None, search=None) -> list[sqlite3.Row]`

Returns expenses for the Expenses History report. All parameters are optional.

- `start_date` / `end_date`: ISO date strings `'YYYY-MM-DD'`. Applied as `DATE(expense_datetime) BETWEEN ? AND ?`.
- `category`: exact match `COLLATE NOCASE`.
- `search`: `LIKE '%{search}%' COLLATE NOCASE` across expense_number, category, description, notes.

Results ordered `expense_datetime DESC, id DESC`.

---

### `get_distinct_categories() -> list[str]`

Returns `SELECT DISTINCT category FROM Expenses COLLATE NOCASE ORDER BY category`. Returns a plain list of strings (not `sqlite3.Row`).

---

### `get_total_expenses(start_date=None, end_date=None) -> float`

Returns `COALESCE(SUM(amount), 0.0)` over all expenses (or filtered by date range on `expense_datetime`).
