# Research: UI Layout Polish

**Date**: 2026-06-29 | **Feature**: [spec.md](spec.md)

## Summary

This is a UI-only layout refinement feature for an existing PySide6 desktop application with a fixed technology stack (Constitution II). There are no external integrations, no new data models, and no ambiguous technology choices to research. All decisions are deterministic given the existing codebase and the clarifications recorded in the spec.

---

## Decision Log

### D1: Actions Column Sizing Strategy

**Decision**: Fixed pre-calculated column width (`_ACTIONS_COL_WIDTH = 170 px`), set once at build time.

**Rationale**: Determined by the widest button combination in the Products table: "Edit" (~40 px) + "Deactivate" (~75 px) + inter-button spacing (~16 px) + cell horizontal padding (~16 px each side) = ~163 px, rounded up to 170. Using a constant avoids `QHeaderView.ResizeToContents` mode, which recalculates on every data load and can produce layout jitter when the set of visible rows changes (e.g., toggling "Show Inactive" switches between "Delete" and "Activate" labels). A fixed constant is stable, deterministic, and consistent with how all other fixed-width columns in the app are handled.

**Alternatives considered**:
- `QHeaderView.ResizeToContents` — rejected: recalculates per load, layout jitter when button label changes.
- Per-row auto-sizing — rejected: QTableWidget does not support per-row column widths; would require custom delegate complexity.

---

### D2: Horizontal Scroll at Minimum Window Width

**Decision**: When the Products table (or any wide table) cannot fit all columns at 900 px, a horizontal scrollbar appears on the table viewport only. The page itself never scrolls horizontally. The Actions column is always the rightmost column and scrolls into view.

**Rationale**: This is the standard behaviour of professional desktop accounting software (QuickBooks, Manager.io) at narrow window widths. Qt's default `QAbstractScrollArea` behaviour produces exactly this when `setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)` is used (which `apply_table_style()` already sets). No additional work is needed beyond confirming the policy is active.

**Alternatives considered**:
- Hide lower-priority columns at narrow widths — rejected: adds conditional layout logic; requires defining column priority; unnecessary complexity for a single-user local app.
- Force all columns to fit via ellipsis truncation — rejected: "Deactivate" text truncated to unreadable length; violates FR-1.3 (buttons must not clip text).

---

### D3: Add-Item Card Structure

**Decision**: Keep the bordered `QFrame` card container on all three form pages (Sales, Purchases, Expenses). Fix the internal QHBoxLayout so all controls share equal height and consistent `spacing_md` between them.

**Rationale**: The card border visually distinguishes the "input area" from the "results table" below it — the same pattern used in QuickBooks Desktop invoice entry. Removing the card would save ~2 px of border but lose the visual anchor that helps users scan the page. The problem was never the card; it was the inconsistent internal layout.

**Alternatives considered**:
- Borderless flat toolbar — rejected: loses visual grouping; makes input row harder to distinguish from page background at a glance.

---

### D4: Adaptive Table Height Implementation

**Decision**: Use the existing `apply_table_style()` + `_fit_table_height()` mechanism in `theme.py`, which wires `rowsInserted`, `rowsRemoved`, and `modelReset` model signals to a deferred `setFixedHeight()` call.

**Rationale**: Already implemented and working (confirmed in prior session). The `QTimer.singleShot(0, ...)` deferral ensures the header has been laid out before the height is calculated, avoiding a zero-height initial render. The `_TABLE_MAX_HEIGHT = 390 px` cap (~12 rows) is appropriate for the screen real estate available at 1280x800.

**Alternatives considered**:
- `QAbstractScrollArea.AdjustToContents` + `QSizePolicy.Maximum` — tried and rejected in prior session: Qt's Maximum policy only prevents growth when other widgets need the space; without a competing widget, the table still expanded.

---

### D5: Button Minimum Width

**Decision**: Each action button in a table cell gets an explicit `setMinimumWidth()` call sized to its label text. For consistency, use these constants:
- "Edit" — 55 px minimum
- "Delete" — 60 px minimum
- "Deactivate" — 85 px minimum
- "Activate" — 70 px minimum
- "Remove" — 70 px minimum

**Rationale**: Qt's default button sizing can be narrower than the text on some Windows themes, producing clipped text. Explicit minimums prevent this. Values are based on approximate character width at 10pt with 8 px horizontal padding each side.

**Alternatives considered**:
- Pure QSS `min-width` — would work for uniform buttons but cannot target individual buttons by label text without custom object names; explicit `setMinimumWidth()` is simpler.
