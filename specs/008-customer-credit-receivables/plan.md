# Implementation Plan: Customer Credit & Receivables Management

**Branch**: `008-customer-credit-receivables` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-customer-credit-receivables/spec.md`

## Summary

Extend the accounting system to track partial invoice payments, maintain a dedicated Customer registry, record post-sale payment collections, and surface receivables data on the Dashboard, a new Customers page, and the Reports section. The implementation follows the existing layered architecture: new `customers_db.py` and `payments_db.py` data-access modules, a new `logic/customers_logic.py` business-logic module, and new/updated UI pages — all without duplicating any existing business logic.

## Technical Context

**Language/Version**: Python 3.x (project-pinned)

**Primary Dependencies**: PySide6 (UI), sqlite3 (standard library, data access)

**Storage**: SQLite via `database.py` connection helper — two new tables (`Customers`, `Payments`) and two new columns on `Sales` (`customer_id`, `amount_paid`). `remaining_balance` is NOT stored — always derived. `Payments` links to both `customer_id` and `sale_id`.

**Testing**: Manual end-to-end validation per `quickstart.md`

**Target Platform**: Windows desktop (single-user, local)

**Project Type**: Desktop application

**Performance Goals**: Customers page loads ≤2 seconds for up to 1,000 customers; dashboard KPIs refresh on every page load

**Constraints**: No ORM, no networking, no third-party libraries beyond PySide6; all SQL parameterized; multi-step operations in single transactions

**Scale/Scope**: Single-user, up to ~1,000 customers; 9 new/modified source files; 1 new nav page; 2 new dialogs

## Constitution Check

*GATE: Must pass before implementation. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Layered Architecture | ✅ PASS | New `customers_db.py`, `payments_db.py` in data layer; `logic/customers_logic.py` in logic layer; UI files import only logic layer |
| II. Fixed Technology Stack | ✅ PASS | Python + PySide6 + SQLite only; no ORM, no networking |
| III. Single-User Scope | ✅ PASS | No roles, no registration; customer statement printing deferred per constitution |
| IV. Financial Data Integrity | ✅ PASS | Invoices never deleted; payments immutable; balance derived from source records; voiding preserves payment history |
| V. Fail Safely | ✅ PASS | All input validated before DB; every DB error shown via QMessageBox; payment ops wrapped in transactions |
| Phase Completion Rule | ✅ PASS | Builds bottom-up: DB schema → data access → logic → UI; app runnable at each step |
| Confirmation Dialog Policy | ✅ PASS | No destructive deletions in this feature; no new confirmation dialogs required |
| UI Behavior Constraints | ✅ PASS | No new fixed-size windows; busy cursor on save/payment operations |

**No violations. No complexity tracking required.**

## Project Structure

### Documentation (this feature)

```text
specs/008-customer-credit-receivables/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   ├── customers_db.md
│   ├── customers_logic.md
│   ├── customers_page.md
│   └── dashboard_update.md
└── tasks.md             ← Phase 2 output (/speckit-tasks)
```

### Source Code Changes

```text
accounting_system/
├── database.py                        MODIFY — add Customers, Payments tables; add columns to Sales
├── customers_db.py                    NEW    — data-access for Customers table
├── payments_db.py                     NEW    — data-access for Payments table
├── sales_db.py                        MODIFY — insert_sale_with_items accepts customer_id, amount_paid (no remaining_balance column)
├── logic/
│   ├── customers_logic.py             NEW    — customer CRUD, balance derivation, payment validation
│   └── sales_logic.py                 MODIFY — add partial-payment validation helpers
├── ui/
│   ├── main_window.py                 MODIFY — add Customers nav button (index 6, after Expenses, before Reports)
│   ├── sales_page.py                  MODIFY — replace customer QLineEdit with searchable customer selector + partial-payment fields
│   ├── customers_page.py              NEW    — customer list with search/sort/filter; highlight customers with balance
│   ├── customer_detail_page.py        NEW    — customer profile: summary cards + invoice table + payment history tab
│   ├── receive_payment_dialog.py      NEW    — modal dialog for collecting a customer payment
│   ├── dashboard_page.py              MODIFY — add Outstanding Receivables and Customers With Balance KPI cards
│   └── reports_page.py               MODIFY — add Customer Receivables report tab
```
