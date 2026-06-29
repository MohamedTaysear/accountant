# Implementation Plan: UI Layout Polish

**Branch**: `001-ui-layout-polish` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-ui-layout-polish/spec.md`

---

## Summary

Polish the layout of the Store Accounting System's PySide6 desktop UI across all pages and dialogs. The primary gaps are: clipped/invisible action buttons in the Products table Actions column, inconsistent control heights, poor alignment on several pages, and large empty containers from fixed-height widgets. The approach is to tighten the central `theme.py` design system first, then apply per-page fixes top-to-bottom, and finish with a full button-visibility audit across all dialogs. No business logic, database, or navigation changes are made.

---

## Technical Context

**Language/Version**: Python 3.11 / PySide6 6.x

**Primary Dependencies**: PySide6 (Qt6) — QVBoxLayout, QHBoxLayout, QHeaderView, QSizePolicy, QFrame, QTableWidget

**Storage**: N/A — layout-only feature; no database changes

**Testing**: Manual visual testing against success criteria in spec; no automated test suite

**Target Platform**: Windows 10+, standard 96 DPI, minimum window 900×600 px, reference window 1280×800 px

**Project Type**: Desktop GUI application (PySide6)

**Performance Goals**: N/A — layout rendering is synchronous and imperceptibly fast

**Constraints**: No new Python packages; no QSS colour or font-size token changes; no business logic changes; all work stays within `accounting_system/ui/`

**Scale/Scope**: 14 source files in `accounting_system/ui/`; 6 pages + 4 dialogs

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| **I. Layered Architecture** | PASS | All changes are in `ui/` files only. No imports of `sqlite3`, `*_db.py`, or logic files are added. |
| **II. Fixed Tech Stack** | PASS | Python + PySide6 only. No new packages introduced. |
| **III. Single-User / Single-Release** | PASS | No new features, no new pages, no deferred Blueprint items. |
| **IV. Financial Data Integrity** | PASS | No invoice, stock, or calculation logic touched. |
| **V. Fail Safely** | PASS | No error-handling paths removed or altered. |
| **UI Behavior Constraints** | PASS | Minimum window size (900x600) preserved; no busy-cursor or focus-behavior changes. |

**No violations. Gate open.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-ui-layout-polish/
├── plan.md              <- this file
├── research.md          <- Phase 0 (resolved)
├── data-model.md        <- Phase 1 (N/A - UI only, no entities)
├── quickstart.md        <- Phase 1 (validation guide)
└── tasks.md             <- Phase 2 (/speckit-tasks - not yet created)
```

### Source Code (repository root)

```text
accounting_system/
└── ui/
    ├── theme.py                  # Central design system - touched first
    ├── products_page.py          # Actions column + header alignment
    ├── sales_page.py             # Add-item card layout tightening
    ├── purchases_page.py         # Add-item card layout tightening
    ├── expenses_page.py          # Add-item card layout tightening
    ├── dashboard_page.py         # KPI card alignment + table sizing
    ├── reports_page.py           # Section panels (mostly done)
    ├── product_dialog.py         # Button visibility audit
    ├── invoice_detail_dialog.py  # Button visibility audit
    ├── expense_detail_dialog.py  # Button visibility audit
    └── change_password_dialog.py # Button visibility audit
```

**Structure Decision**: Single `ui/` package. All modifications stay within this package. No new modules are introduced.

---

## Implementation Phases

### Phase A - Theme Foundations (`theme.py`)

**Goal**: All global layout constants and helpers correct before any page is touched.

| Task | What | Why |
|------|------|-----|
| A1 | Add `_ACTIONS_COL_WIDTH = 170` constant (sized to "Edit" + "Deactivate" + button spacing) | FR-1.1 - fixed Actions column width anchored to widest label |
| A2 | Verify all control `min-height` values in QSS are 30 px | FR-5.1, FR-5.2 |
| A3 | Verify `apply_table_style()` wires model signals for adaptive height | FR-3.1-3.4 |
| A4 | Add `apply_actions_column(table, col_index)` helper: sets fixed width to `_ACTIONS_COL_WIDTH`, disables resize on that column section | FR-1.1, avoids duplication |

### Phase B - Products Page (`products_page.py`)

**Goal**: Actions column fully visible; header row aligned; table adaptive.

| Task | What | Why |
|------|------|-----|
| B1 | Call `theme.apply_actions_column(self.table, col)` for the Actions column | FR-1.1, FR-9.3 |
| B2 | Add `setMinimumWidth` on Edit/Delete/Deactivate/Activate buttons to fit their label | FR-1.2, FR-1.3 |
| B3 | Ensure search input, "Show Inactive" checkbox, and "+ Add Product" button share one HBoxLayout row with AlignVCenter | FR-9.1 |
| B4 | Confirm Name column has QHeaderView.Stretch and no other column stretches | FR-9.2 |
| B5 | Confirm `layout.addStretch()` present after table widget | FR-9.4 |

### Phase C - Form Pages (`sales_page.py`, `purchases_page.py`, `expenses_page.py`)

**Goal**: Add-item card controls equal height; line-item Remove button visible.

| Task | What | Why |
|------|------|-----|
| C1 | Audit add-item card: all labels + inputs + Add button in one QHBoxLayout row with `spacing_md` | FR-7.1 |
| C2 | Call `theme.apply_actions_column(table, remove_col)` on line-item table's Remove column | FR-1.1 - Remove button must not be clipped |
| C3 | Confirm header card, add-item card, and footer card all have `setSizePolicy(Expanding, Fixed)` | FR-7.2, FR-7.3 |
| C4 | Confirm `layout.addStretch()` after footer card | FR-7.4 |
| C5 | Expenses two-row add-card: keep two rows but ensure each row's controls are equal height with AlignVCenter | FR-7.1 variant |

### Phase D - Dashboard Page (`dashboard_page.py`)

**Goal**: KPI cards equal height and aligned; tables adaptive.

| Task | What | Why |
|------|------|-----|
| D1 | KPI card row uses QHBoxLayout with equal stretch factors so all cards share the same width | FR-8.1 |
| D2 | KPI card row left/right margins match table left/right margins | FR-8.2 |
| D3 | Confirm `apply_table_style()` called on Low Stock and Recent Transactions tables | FR-8.3 |
| D4 | Confirm consistent `spacing_lg` between Dashboard sections | FR-8.4 |

### Phase E - Reports Page (`reports_page.py`)

**Goal**: Confirm prior redesign is correct; no regression.

| Task | What | Why |
|------|------|-----|
| E1 | Verify all six section panels use `_section_panel()` with title + separator + filters + table | FR-4.1, FR-4.2 |
| E2 | Verify section panel padding uses `spacing_sm` not `spacing_lg` at top/bottom | FR-4.4 |
| E3 | Confirm adaptive height wired on all six report tables | FR-3 |

### Phase F - Dialogs Button Audit

**Goal**: Every button in every dialog fully visible at 1280x800.

| Task | What | Dialogs |
|------|------|---------|
| F1 | Confirm each dialog's button row: buttons have `setMinimumWidth` matching label; no button cropped | All 4 dialogs |
| F2 | Confirm dialog button rows use QHBoxLayout with `addStretch()` before buttons (right-aligned) | All 4 dialogs |
| F3 | `invoice_detail_dialog.py` - "Void Invoice" and "Close" both visible; Void disabled (not hidden) on voided invoices | FR-12.2 |
| F4 | `product_dialog.py` - "Save" and "Cancel" visible at all dialog sizes | FR-12.2 |
| F5 | `change_password_dialog.py` - "Change Password" and "Cancel" fully visible | FR-12.2 |
| F6 | `expense_detail_dialog.py` - all action buttons visible | FR-12.2 |

### Phase G - Full Visual Review

**Goal**: Walk every page and dialog against the 7 Success Criteria.

| Check | Criterion | Pass Condition |
|-------|-----------|----------------|
| G1 | Zero clipped buttons | No button text clipped at 1280x800 on any page or dialog |
| G2 | Consistent control height | Any mixed-control row (search + combo + button) all at same visual height |
| G3 | Adaptive tables | Empty table: no white box taller than header + 1 row. 20 rows: internal scroll activates |
| G4 | Reports sections | Six sections: plain bold title, no heavy frame around title |
| G5 | Resize stability | 1280x800 -> 900x600: no clipped controls, no disappearing buttons |
| G6 | Form compactness | Sales/Purchases/Expenses with zero lines: form content <= 50% of 800 px height |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Actions column sizing | Fixed pre-calculated width (`_ACTIONS_COL_WIDTH = 170`) | Deterministic; no layout shifts on data load; "Deactivate" is the widest label |
| Narrow-window overflow | Table-only horizontal scrollbar; Actions always last column | Standard desktop accounting pattern; page never scrolls horizontally |
| Add-item card structure | Keep bordered card; tighten internal layout only | Preserves visual separation of input area from results table below |
| Adaptive table height | Model-signal-driven `setFixedHeight()` in `apply_table_style()` | Wired once in theme; zero per-page changes needed |
| No new packages | All changes use existing PySide6 | Constitution II - fixed tech stack |
