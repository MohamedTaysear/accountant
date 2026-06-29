# Implementation Plan: Design System & UI Modernization

**Branch**: `007-design-system` | **Date**: 2026-06-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-design-system/spec.md`

## Summary

Establish a centralized design system for the store accounting application and apply it uniformly across every screen, dialog, and widget. The core deliverable is a new `ui/theme.py` module built around a `ThemeDefinition` base class and `LightTheme` subclass. This architecture supports adding new themes (Dark, High Contrast) in the future without modifying any screen or dialog file — a future theme is a self-contained `ThemeDefinition` subclass, and switching themes requires only `set_theme()` in `main.py`. Screen files call only the module-level helper API (`apply_table_style()`, `color_for_value()`, etc.) and never access token constants directly. A small `ui/icons/` directory provides bundled SVG icon assets. The global QSS stylesheet is applied once at startup in `main.py`. No business logic, database schema, or workflow changes. No new Python packages.

## Technical Context

**Language/Version**: Python 3.11 (existing)

**Primary Dependencies**: PySide6 (existing — stylesheet engine, QIcon, QStyle, QGraphicsDropShadowEffect, Qt.ElideRight for text truncation)

**Storage**: SQLite — existing `store.db`, no schema changes

**Testing**: Manual visual validation per `quickstart.md`

**Target Platform**: Windows 10+ desktop (existing)

**Project Type**: Desktop application — visual-only modernization phase

**Performance Goals**: Stylesheet application is a one-time startup cost with no perceptible delay. No new runtime performance requirements.

**Constraints**: No new Python packages. All styling via PySide6 QSS and Python constants in `ui/theme.py`. Icons delivered as bundled SVG files in `ui/icons/`. No business logic, workflow, or schema changes.

**Scale/Scope**: 1 new file (`ui/theme.py`) + `ui/icons/` directory. 15 existing UI files modified. ~15 tables, ~20 KPI cards, ~10 dialogs receive consistent styling.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Layered Architecture | ✅ PASS | `ui/theme.py` is a UI-layer utility imported only by UI files. Contains no SQL, no business logic, no database imports — only style constants, QSS strings, and widget helpers. No new cross-layer imports. |
| II. Fixed Technology Stack | ✅ PASS | No new Python packages. PySide6's built-in stylesheet engine, QIcon, and QStyle are used. SVG assets are data files. All existing SQL, connection, and transaction patterns untouched. |
| III. Single-User Scope | ✅ PASS | Visual-only phase. No new screens, workflows, or user-facing features beyond styling. |
| IV. Financial Data Integrity | ✅ PASS | No changes to the data access or business logic layers. Profit/loss color-coding is read-only presentation with no effect on stored data. |
| V. Fail Safely | ✅ PASS | PySide6 stylesheet failures are non-fatal (widgets fall back to OS defaults). No new I/O paths or exception surfaces. Existing error handling unchanged. |
| Phase Completion Rule | ✅ PASS | Phase is delivered with all screens consistently styled and all existing functionality verified by the quickstart regression pass. No screen is left partially styled. |
| Confirmation Dialog Policy | ✅ PASS | No changes to confirmation dialog behavior — only visual styling of dialogs. |
| UI Behavior Constraints | ✅ PASS | Busy cursor, minimum window size, and keyboard focus behaviors are preserved unchanged. |

**Post-design re-check**: All contracts reviewed against constitution principles — no violations found.

## Project Structure

### Documentation (this feature)

```text
specs/007-design-system/
├── plan.md              # This file
├── research.md          # Decisions: styling mechanism, icon strategy, font, palette, components
├── data-model.md        # Design token model — the public structure of ui/theme.py
├── quickstart.md        # Manual validation guide — visual inspection + regression pass
├── contracts/
│   ├── theme_module.md      # Contract for ui/theme.py (tokens, constants, helpers)
│   └── screen_styling.md    # How each screen/dialog applies the theme
└── tasks.md             # Output of /speckit-tasks (not created by /speckit-plan)
```

### Source Code (repository root)

```text
accounting_system/
├── main.py                          # MODIFIED: apply global QSS stylesheet at startup
└── ui/
    ├── theme.py                     # NEW: centralized design system module
    ├── icons/                       # NEW: bundled SVG icon assets
    │   ├── dashboard.svg
    │   ├── products.svg
    │   ├── sales.svg
    │   ├── purchases.svg
    │   ├── expenses.svg
    │   └── reports.svg
    ├── login_window.py              # MODIFIED: theme applied
    ├── main_window.py               # MODIFIED: sidebar and nav button styling
    ├── dashboard_page.py            # MODIFIED: KPI card styling, profit/loss colors
    ├── products_page.py             # MODIFIED: table + form styling
    ├── product_dialog.py            # MODIFIED: dialog styling
    ├── purchases_page.py            # MODIFIED: table + form styling
    ├── sales_page.py                # MODIFIED: table + form styling
    ├── expenses_page.py             # MODIFIED: table + form styling
    ├── reports_page.py              # MODIFIED: table + summary styling
    ├── invoice_detail_dialog.py     # MODIFIED: dialog + table styling
    ├── expense_detail_dialog.py     # MODIFIED: dialog + table styling
    ├── change_password_dialog.py    # MODIFIED: dialog styling
    └── expenses_report_page.py      # MODIFIED: table styling
```

**Structure Decision**: Single desktop project. One new module (`ui/theme.py`) and one new asset directory (`ui/icons/`). All other changes are modifications to existing files. Implementation order: `theme.py` → global stylesheet in `main.py` → screen-by-screen application.

## Complexity Tracking

> No constitution violations — no entries required.
