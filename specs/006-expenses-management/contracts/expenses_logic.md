# Contract: expenses_logic

**Layer**: Logic
**File**: `accounting_system/logic/expenses_logic.py`
**Imports**: `expenses_db` only (no PySide6, no direct `database` or SQL)

---

## Functions

### `validate_expense(expense_datetime, category, description, amount) -> list[str]`

Returns a list of human-readable error strings. Empty list = valid.

Rules:
- `category.strip()` must be non-empty → "Category is required."
- `description.strip()` must be non-empty → "Description is required."
- `amount` must be a number > 0 → "Amount must be greater than zero."

`expense_datetime` is always provided (defaulted by the UI) and is not validated here.

---

### `add_expense(expense_datetime, category, description, amount, notes) -> str`

Validates, then calls `expenses_db.insert_expense(...)`. Returns the generated expense number.

Raises `ValueError` with joined error messages if validation fails.

---

### `update_expense(expense_id, expense_datetime, category, description, amount, notes) -> None`

Validates, then calls `expenses_db.update_expense(...)`.

Raises `ValueError` if validation fails.

---

### `delete_expense(expense_id) -> None`

Calls `expenses_db.delete_expense(expense_id)`. No additional business rules.

---

### `get_expenses(search=None) -> list`

Delegates to `expenses_db.get_all_expenses(search)`.

---

### `get_expenses_for_report(start_date=None, end_date=None, category=None, search=None) -> list`

Delegates to `expenses_db.get_expenses_for_report(...)`.

---

### `get_categories() -> list[str]`

Delegates to `expenses_db.get_distinct_categories()`.

---

## report_logic additions

**File**: `accounting_system/logic/report_logic.py` (existing file, new functions added)

### `get_today_expenses() -> float`
Calls `expenses_db.get_total_expenses(start_date=today, end_date=today)`.

### `get_this_month_expenses() -> float`
Calls `expenses_db.get_total_expenses(start_date=first_of_month, end_date=today)`.

### `get_net_profit() -> float`
Returns `get_total_profit() - expenses_db.get_total_expenses()`. Rounded to 2 decimal places.
