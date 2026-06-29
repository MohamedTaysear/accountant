# Implementation Plan: Expenses Management

**Branch**: `006-expenses-management` | **Date**: 2026-06-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-expenses-management/spec.md`

## Summary

Add a complete Expenses Management module to the store accounting system. Expenses represent operating costs (rent, salaries, utilities) and are entirely independent from the inventory-purchasing workflow. The feature adds a dedicated database table, a CRUD page, a standalone report page, three new Dashboard KPI cards (Today's Expenses, This Month Expenses, Net Profit), and a smart case-insensitive category autocomplete — all within the existing Python / PySide6 / SQLite layered architecture.

## Technical Context

**Language/Version**: Python 3.11 (existing)

**Primary Dependencies**: PySide6 (UI), sqlite3 stdlib (data access)

**Storage**: SQLite — single `store.db` file via `database.py`

**Testing**: Manual validation per `quickstart.md`

**Target Platform**: Windows desktop (existing)

**Project Type**: Desktop application

**Performance Goals**: Dashboard cards update within 1 second; expense save/delete imperceptible delay for a single-user SQLite workload

**Constraints**: No ORM, no networking, no new third-party dependencies; all SQL parameterized; single short-lived connection per operation; multi-step writes in transactions

**Scale/Scope**: Single user, single machine, hundreds to low-thousands of expense records

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Layered Architecture | ✅ PASS | `expenses_db.py` → data only; `logic/expenses_logic.py` → business rules only; `ui/expenses_page.py` / `ui/expenses_report_page.py` → display only. No SQL in UI. No PySide6 in logic. |
| II. Fixed Technology Stack | ✅ PASS | Python + PySide6 + SQLite only. No ORM, no new libs. All SQL parameterized. Transactions wrap the insert+update numbering pattern. |
| III. Single-User Scope | ✅ PASS | No multi-user, no roles, no registration. Expenses is a complete feature, not deferred. |
| IV. Financial Data Integrity | ✅ PASS | Expenses are not invoices; hard-delete is appropriate per spec. `SaleItems.purchase_price_at_sale` and existing profit calculations are untouched. Net Profit = `get_total_profit() - get_total_expenses()` — a read-only derived value. |
| V. Fail Safely | ✅ PASS | Validation in logic layer before any DB call. All DB errors caught in UI with `QMessageBox.critical`. Busy cursor for save/delete/CSV export operations. |
| Phase Completion Rule | ✅ PASS | Phase delivered as a runnable, demoable unit; quickstart covers all manual checkpoints. |
| Confirmation Dialog Policy | ✅ PASS | Delete requires confirmation. Add/Edit do not. |
| UI Behavior Constraints | ✅ PASS | Busy cursor for expense save, delete, CSV export. Main window remains resizable (no changes to window sizing). |

**Post-design re-check**: All contracts reviewed against constitution principles — no violations found.

## Project Structure

### Documentation (this feature)

```text
specs/006-expenses-management/
├── plan.md              # This file
├── research.md          # Decisions: numbering, timestamps, categories, sort order, dashboard, report placement
├── data-model.md        # Expenses table DDL + key queries
├── quickstart.md        # Manual validation guide (7 sections, 30+ checkpoints)
├── contracts/
│   ├── expenses_db.md          # Data access layer contract
│   ├── expenses_logic.md       # Logic layer contract (+ report_logic additions)
│   ├── expenses_page.md        # ExpensesPage + ExpenseDialog UI contracts
│   ├── expenses_report_page.md # ExpensesReportPage + ExpenseDetailDialog UI contracts
│   ├── dashboard_update.md     # DashboardPage modification contract
│   └── main_window_update.md   # MainWindow modification contract
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code

```text
accounting_system/
├── database.py                        # MODIFY: add Expenses table DDL to initialize_database()
├── expenses_db.py                     # NEW: data access for Expenses table
├── logic/
│   ├── __init__.py                    # unchanged
│   ├── expenses_logic.py              # NEW: validation, CRUD delegation, category logic
│   ├── report_logic.py                # MODIFY: add get_today_expenses(), get_this_month_expenses(), get_net_profit()
│   ├── purchase_logic.py              # unchanged
│   └── sales_logic.py                 # unchanged
└── ui/
    ├── expenses_page.py               # NEW: Expenses CRUD page (QWidget)
    ├── expense_dialog.py              # NEW: Add/Edit Expense dialog (QDialog)
    ├── expense_detail_dialog.py       # NEW: Read-only Expense Detail dialog (QDialog)
    ├── expenses_report_page.py        # NEW: Expenses History report page (QWidget)
    ├── dashboard_page.py              # MODIFY: add 3 new KPI cards + refresh calls
    ├── main_window.py                 # MODIFY: add Expenses + Expenses Report sidebar buttons + pages
    └── [existing files unchanged]
```

**Structure Decision**: Single-project layout (existing). New files follow the established `*_db.py` / `logic/*.py` / `ui/*.py` naming convention. No new directories (logic/ and ui/ already exist).

## Implementation Order

Build strictly bottom-up per the Constitution's Phase Completion Rule:

1. **Foundation** — `database.py`: add `Expenses` table DDL.
2. **Data Access** — `expenses_db.py`: all DB functions per contract.
3. **Logic** — `logic/expenses_logic.py`: validation + CRUD + category delegation.
4. **Logic** — `logic/report_logic.py`: add 3 new functions.
5. **UI dialogs** — `ui/expense_dialog.py` (Add/Edit), `ui/expense_detail_dialog.py` (read-only).
6. **UI pages** — `ui/expenses_page.py` (CRUD page), `ui/expenses_report_page.py` (report page).
7. **UI integration** — `ui/dashboard_page.py` (new cards), `ui/main_window.py` (sidebar + stack).
8. **Validation** — Run full quickstart.md checklist.

## Complexity Tracking

No constitution violations. No complexity justification required.
