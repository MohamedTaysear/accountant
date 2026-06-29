# Implementation Plan: Phase 4 — Sales

**Branch**: `004-sales` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-sales/spec.md`

## Summary

Replace the Sales page placeholder with a fully functional sales-invoice creation screen. The user builds a multi-line invoice against real stock produced in Phase 3, applies an optional discount, and saves — atomically decrementing stock for every sold product. Three new files are created bottom-up: `sales_db.py` (raw SQL), `logic/sales_logic.py` (validation + calculations), and `ui/sales_page.py` (replaces placeholder). All patterns mirror the already-complete Phase 3 Purchases implementation.

## Technical Context

**Language/Version**: Python 3.x (same as all prior phases)

**Primary Dependencies**: PySide6 (UI), sqlite3 stdlib (database) — no new dependencies

**Storage**: SQLite via `database.py` — `Sales` and `SaleItems` tables already created in Phase 1; no schema changes required

**Testing**: Manual testing only per Implementation Plan checkpoints (no automated test framework)

**Target Platform**: Windows 10, single local machine, single Admin user

**Project Type**: Desktop application (PySide6)

**Performance Goals**: Save Invoice completes in well under 1 second on local hardware; wait cursor shown for the full duration

**Constraints**: No new dependencies. No networking. No ORM. All SQL parameterized. Atomic transactions only. UI never imports sqlite3 directly.

**Scale/Scope**: Single user; invoice line count bounded by practical daily use (dozens, not thousands). No pagination or lazy-loading required.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Layered Architecture | ✅ PASS | `ui/sales_page.py` → `logic/sales_logic.py` → `sales_db.py` → `database.py`. No UI→DB direct calls. No SQL in logic layer. |
| II. Fixed Technology Stack | ✅ PASS | Python + PySide6 + SQLite only. No new library introduced. |
| III. Single-User Scope | ✅ PASS | One admin account. No roles. No registration. |
| IV. Financial Data Integrity | ✅ PASS | Save is a single transaction (header + lines + stock decrement). Voiding is Phase 5 scope — not implemented here. |
| V. Fail Safely | ✅ PASS | Stock validation before DB call. Discount validation before save. All exceptions surface via QMessageBox. No raw tracebacks to user. |
| Phase Completion Rule | ✅ PASS | App must remain fully runnable after this phase; Sales page fully wired (no placeholder remains). |
| Confirmation Dialog Policy | ✅ PASS | Clear Invoice requires confirmation only when ≥1 line exists. Save Invoice does not require pre-confirmation. |
| UI Behavior Constraints | ✅ PASS | Wait cursor on Save. Auto-focus Quantity after product selection. Focus returns to product picker after line-add. In-progress invoice retained on navigation. |

**All gates pass. No violations.**

## Project Structure

### Documentation (this feature)

```text
specs/004-sales/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (new files this phase)

```text
accounting_system/
├── sales_db.py                   ← NEW: Data Access layer (raw parameterized SQL)
├── logic/
│   └── sales_logic.py            ← NEW: Business Logic layer (validation, calculations)
└── ui/
    └── sales_page.py             ← REPLACE placeholder: full Sales invoice UI
```

**Structure Decision**: Three-file bottom-up implementation, identical in shape to Phase 3 (Purchases). `sales_db.py` sits at repo root alongside `purchases_db.py`. No new directories needed.

## Complexity Tracking

No Constitution violations. No complexity justification needed.
