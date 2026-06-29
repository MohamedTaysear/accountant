# Research: Expenses Management

**Feature**: 006-expenses-management
**Date**: 2026-06-28

---

## Expense Number Generation

**Decision**: Use the same insert-then-update pattern as Purchases and Sales.

Insert a row with `expense_number = 'PENDING'`, retrieve `last_insert_rowid()`, compute `EXP-{id:06d}`, and immediately update the row in the same transaction.

**Rationale**: Matches the established pattern in `purchases_db.py` and `sales_db.py`. Guarantees uniqueness without a separate sequence table.

**Alternatives considered**: `SELECT MAX(id) + 1` — rejected because it has a TOCTOU gap under concurrent access (not a real concern for this single-user app, but consistency with existing pattern preferred).

---

## Expense Timestamp Handling

**Decision**: Store user-editable `expense_datetime` (type TEXT, format `YYYY-MM-DD HH:MM:SS`) separately from the immutable `created_at` audit timestamp.

**Rationale**: `database.now_cairo()` produces `YYYY-MM-DD HH:MM:SS` in Egypt local time. The Add/Edit dialog defaults `expense_datetime` to the current Cairo time but allows override. `created_at` is set once at insert and never updated. Both fields mirror the pattern used across existing tables.

---

## Category Autocomplete (Case-Insensitive)

**Decision**: Derive categories dynamically via `SELECT DISTINCT category FROM Expenses COLLATE NOCASE ORDER BY category`. Store the category exactly as the user first typed it (original casing). Match suggestions case-insensitively using `QCompleter` with `Qt.CaseInsensitive` match mode on the `QComboBox`.

**Rationale**: No separate Category table is needed. A `DISTINCT … COLLATE NOCASE` query on the Expenses table returns one row per canonical category. The user's original casing is preserved in the first-saved record; subsequent saves with different casing save the new casing (they are treated as the same suggestion, but the stored value reflects what was typed each time — acceptable for a free-text field).

**Alternatives considered**: Separate `ExpenseCategories` table — rejected per spec (no separate Category Management screen) and to keep the schema minimal.

---

## Default Sort Order

**Decision**: Expenses table on the Expenses page sorts by `expense_datetime DESC` by default (clarified in session 2026-06-28).

**Rationale**: Consistent with Sales and Purchases pages; the accountant most commonly needs the most recent entry visible without scrolling.

---

## Dashboard Integration

**Decision**: Add three new `QLabel` cards to `DashboardPage` using the existing `_make_card()` helper. Add three new functions to `logic/report_logic.py`:

- `get_today_expenses() -> float` — delegates to `expenses_db`
- `get_this_month_expenses() -> float` — delegates to `expenses_db`
- `get_net_profit() -> float` — `get_total_profit() - get_total_expenses()`

`DashboardPage._refresh()` calls these three new functions alongside the existing ones.

**Rationale**: Zero change to existing profit-card logic (today/month/total profit cards continue using `sales_db`). Net Profit is all-time only (no time-bounded variant).

**Net Profit color coding**: Positive → green (`#2e7d32`); zero or negative → default bold (same pattern as profit cards).

---

## Expenses History Report

**Decision**: Implement as a standalone `ExpensesReportPage` added to the sidebar as a new "Expenses Report" entry (sidebar index 6). This avoids modifying the existing `ReportsPage`.

**Rationale**: The existing `ReportsPage` is already at capacity (Sales + Purchases side by side + top-products panels). Adding a third panel would be cramped. A dedicated page gives Expenses History the same full-width layout as Sales/Purchases History individually. The `expenses.md` report requirements (date filter, category filter, search, detail dialog, CSV export) map cleanly to a standalone page modeled on `ReportsPage`.

**Alternatives considered**: Tab widget inside `ReportsPage` — rejected to avoid modifying working code and to keep the change set minimal.

---

## Expense Detail Dialog

**Decision**: Read-only dialog (`ExpenseDetailDialog`) that shows all expense fields. Modeled on `InvoiceDetailDialog`. Opened by double-clicking a row in `ExpensesReportPage`.

**Rationale**: Follows spec requirement ("Expense Detail dialog") and existing double-click behavior in `ReportsPage`.

---

## Add/Edit Expense Dialog

**Decision**: Single `ExpenseDialog` class that handles both add and edit modes (receives `expense_id=None` for add, an integer for edit). Contains: `QDateTimeEdit` (expense_datetime, default = `now_cairo()`), `QComboBox` editable (category), `QLineEdit` (description), `QDoubleSpinBox` (amount, min=0.01, decimals=2), `QTextEdit` or `QLineEdit` (notes, optional).

**Rationale**: Single dialog class for both add and edit matches the pattern used by `ProductDialog`. Pre-populates fields when editing.

---

## Architecture Compliance

All new code follows the existing layered pattern:

| Layer | New File(s) | Imports |
|-------|-------------|---------|
| Foundation | `database.py` (Expenses table added) | — |
| Data Access | `expenses_db.py` | `database` only |
| Logic | `logic/expenses_logic.py` | `expenses_db` only; no PySide6 |
| Logic (update) | `logic/report_logic.py` | `expenses_db` added |
| UI | `ui/expenses_page.py` | `logic.expenses_logic` |
| UI | `ui/expense_dialog.py` | (no direct DB/logic import; fields only) |
| UI | `ui/expense_detail_dialog.py` | `expenses_db` (read-only display) OR via logic |
| UI | `ui/expenses_report_page.py` | `logic.expenses_logic`, `expenses_db` |
| UI (update) | `ui/dashboard_page.py` | `logic.report_logic` (existing import) |
| UI (update) | `ui/main_window.py` | new page classes |

No SQL in UI files. No PySide6 in logic files. No circular imports.
