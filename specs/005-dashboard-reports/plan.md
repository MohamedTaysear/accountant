# Implementation Plan: Dashboard & Reports

**Branch**: `005-dashboard-reports` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-dashboard-reports/spec.md`

## Summary

Replace the Dashboard and Reports placeholder pages, and add the Invoice Detail Dialog. The Dashboard shows ten summary cards (product counts, inventory value, potential stock profit, today's financials, all-time profit, low stock count), a clickable Low Stock list, a Recent Activity feed of the 10 latest invoices, and color-coded visual indicators. The Reports page provides date-filtered financial summaries, Sales/Purchases history tables, Top Selling and Top Purchased Products panels, CSV export of the active history table, and access to the Invoice Detail Dialog (which shows historical cost and profit-per-line for sales and supports void + print). All profit calculations use `SaleItems.purchase_price_at_sale` — never the current `Products.purchase_price`.

## Technical Context

**Language/Version**: Python 3.x (matching existing project)

**Primary Dependencies**: PySide6 (Qt for Python), SQLite3 (stdlib), csv (stdlib), datetime (stdlib)

**Storage**: SQLite — `data/store.db`. Schema fully established in Phases 1–4. No migrations required for this phase.

**Testing**: Manual testing per the Phase 5 checkpoint in `IMPLEMENTATION_PLAN.md`

**Target Platform**: Windows 10, single local desktop

**Project Type**: Desktop application (PySide6/Qt)

**Performance Goals**: All Dashboard card reads and Reports filter updates complete in under one second on local hardware.

**Constraints**: No new database columns or tables. No third-party libraries. All SQL parameterized. No circular imports (UI → Logic → DB → Foundation only).

**Scale/Scope**: Single user, single local SQLite database. No concurrency concerns.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Layered Architecture | ✅ PASS | `dashboard_page.py` and `reports_page.py` call `report_logic.py`; no direct sqlite3 imports in UI. `invoice_detail_dialog.py` calls `sales_logic`/`purchase_logic` for void. |
| II. Fixed Technology Stack | ✅ PASS | Python, PySide6, SQLite, stdlib csv, Qt QPrinter only. No ORM, no third-party libs. |
| III. Single-User / Single-Release | ✅ PASS | No multi-user features. All Blueprint-scoped functionality is included now. |
| IV. Financial Data Integrity | ✅ PASS | Profit always uses `purchase_price_at_sale`. Void-only correction model preserved. Voided invoices kept in history. |
| V. Fail Safely | ✅ PASS | All DB errors, void conflicts, export failures, and print failures must surface as friendly QMessageBox messages. No raw tracebacks. |
| Phase Completion Rule | ✅ PASS | App must remain fully runnable at end of phase. All five pages functional. |
| Confirmation Dialog Policy | ✅ PASS | Void Invoice requires confirmation. Print and CSV Export do not. |
| UI Behavior Constraints | ✅ PASS | Wait cursor on Void, Print, CSV Export. Dashboard refreshes on showEvent. No progress bars. |

**Post-design re-check**: No violations introduced. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/005-dashboard-reports/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
│   ├── report_logic.md
│   ├── dashboard_page.md
│   ├── reports_page.md
│   └── invoice_detail_dialog.md
└── tasks.md             ← Phase 2 output (/speckit-tasks — not created here)
```

### Source Code

```text
accounting_system/
├── logic/
│   └── report_logic.py          ← NEW: aggregation functions (Total Sales, Purchases, Profit)
├── ui/
│   ├── dashboard_page.py        ← REPLACE placeholder: 10 cards, Low Stock list, Recent Activity
│   ├── invoice_detail_dialog.py ← NEW: Sales/Purchases read-only detail, Void, Print
│   └── reports_page.py          ← REPLACE placeholder: date filter, summaries, history, Top Products, CSV export
├── sales_db.py                  ← EXISTING (read-only in this phase)
├── purchases_db.py              ← EXISTING (read-only in this phase)
└── products_db.py               ← EXISTING (read-only in this phase)
```

**Structure Decision**: Single-project layout matching existing codebase. Four files to create/replace, zero new files in `logic/` beyond `report_logic.py`, zero schema changes.

## Build Order (bottom-up, per Constitution §Phase Completion Rule)

| Step | File | Type | Depends On |
|---|---|---|---|
| 1 | `logic/report_logic.py` | NEW | `sales_db.py`, `purchases_db.py` |
| 2 | `ui/invoice_detail_dialog.py` | NEW | `sales_db.py`, `purchases_db.py`, `sales_logic.py`, `purchase_logic.py` |
| 3 | `ui/reports_page.py` | REPLACE | `report_logic.py`, `invoice_detail_dialog.py` |
| 4 | `ui/dashboard_page.py` | REPLACE | `products_db.py`, `sales_db.py`, `purchases_db.py`, `report_logic.py` |
