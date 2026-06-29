# Specification: UI Layout Polish

**Feature**: UI Layout Polish & Button Visibility  
**Short Name**: ui-layout-polish  
**Feature Directory**: specs/001-ui-layout-polish  
**Status**: Draft  
**Created**: 2026-06-29  

---

## Overview

The Store Accounting System (a PySide6 desktop application) has a complete design system and working business logic, but several persistent layout and usability problems remain across all pages. This feature addresses those problems through UI-only refinements — improving table layouts, fixing invisible/clipped action buttons, standardising control heights, tightening alignment, removing unnecessary empty space, and ensuring every interactive element is fully visible at all supported window sizes.

No business logic, database logic, calculations, workflows, or navigation are changed.

---

## Clarifications

### Session 2026-06-29

- Q: Should the add-item row (Product + Qty + Price + Add button) keep its bordered card container or become a flat borderless toolbar? → A: Keep the bordered card container; fix the internal layout so all controls share equal height and consistent spacing. The card border and background are preserved.
- Q: At the 900 px minimum window width, when the Products table cannot display all columns simultaneously, which strategy applies? → A: A horizontal scrollbar appears on the table viewport only; the page itself never scrolls horizontally. The Actions column is always the last column and scrolls into view — it is never hidden.
- Q: For the Actions column, when rows have different button combinations (Edit+Delete vs Edit+Deactivate vs Edit+Activate), how should the column be sized? → A: Fixed column width pre-calculated to fit the widest button label ("Deactivate"); width set once in code, not auto-sized by Qt per load.

---

## Problem Statement

Users experience the following usability failures in the current UI:

1. **Invisible or clipped action buttons** — Edit/Delete/Deactivate buttons inside the Products table Actions column are partially hidden, clipped by cell boundaries, or extend outside their parent cells, making them unusable.
2. **Inconsistent table quality** — Row heights, cell padding, header spacing, and column sizing vary across pages and do not meet the standard expected of professional desktop accounting software.
3. **Fixed-height containers** — Several widgets use hard-coded heights, creating large empty areas when content is sparse and causing overflow when content grows.
4. **Oversized section headers on the Reports page** — Section titles sit inside heavy bordered frames, consuming vertical space disproportionate to their content.
5. **Inconsistent control heights** — Search boxes, combo boxes, line edits, spin boxes, and buttons have different visual heights, making forms look unpolished.
6. **Poor alignment** — Controls on the same page do not share consistent left/right edges, margins, or vertical rhythm.
7. **Spacing problems on form pages** — The Sales, Purchases, and Expenses invoice entry pages have gaps between form controls that make them feel disjointed rather than like a single cohesive toolbar.
8. **Partially clipped or invisible buttons** across dialogs and pages at various window sizes.

---

## Goals

- Every button in the application is fully visible and accessible at all supported window sizes.
- Every table matches the visual quality of professional desktop accounting software (Manager.io / QuickBooks Desktop level).
- All input controls share a single standard height.
- All pages use adaptive layouts — no large empty containers when content is sparse.
- The Reports page presents each section as a clean vertical flow: Title → Filters → Table.
- Form pages (Sales, Purchases, Expenses) present their entry controls as a compact, aligned toolbar row.
- Every page passes a full visual review with zero clipped controls, zero overlapping widgets, and zero missing buttons.

---

## Out of Scope

- Business logic, database queries, or calculation changes.
- Navigation structure or page routing.
- New features, new pages, or new workflows.
- Color scheme or brand identity changes (design tokens remain as-is).
- Adding new UI controls not already present.
- Authentication, export, printing, or backup/restore logic.

---

## User Scenarios & Testing

### Scenario 1 — Products page: Action buttons are always usable

**Given** the Products page contains one or more products  
**When** the user views the table at the default window size (1280×800)  
**Then** the Edit button and the Delete/Deactivate/Activate button for each row are fully visible inside the Actions column, with no clipping, no overflow, and no overlap.

**Also When** the user resizes the window to its minimum supported width  
**Then** the Actions column scrolls or the action buttons remain fully visible — they are never cropped.

### Scenario 2 — Sales page: Add-item toolbar feels cohesive

**Given** the Sales invoice entry page is open  
**When** the user views the Product selector, Qty field, and "+ Add to Invoice" button  
**Then** all three controls have equal visual height, are vertically centred, and share equal horizontal spacing — the row reads as a single toolbar.

### Scenario 3 — Reports page: Sections are readable at a glance

**Given** the Reports page is open  
**When** the user scans the History section  
**Then** each section title ("Sales History", "Purchases History", "Expenses History") is displayed as a bold plain heading — not inside a heavy bordered container — followed immediately by a search field and then the table.

### Scenario 4 — Adaptive table height

**Given** a table contains only 1 row of data  
**When** the page renders  
**Then** the table occupies only the vertical space needed to display that row and its header — no large white empty area below the last row.

**Given** the same table then receives 20 rows of data  
**When** the page re-renders  
**Then** the table grows to a maximum comfortable height and enables internal vertical scrolling for the overflow.

### Scenario 5 — Consistent control heights

**Given** any page that contains a search box, a combo box, and a button side by side  
**When** the user views that row  
**Then** all three controls have the same visual height, appearing on the same baseline.

### Scenario 6 — Window resize: no clipping

**Given** the application is running at 1280×800  
**When** the user resizes the window to 900×600  
**Then** no button disappears, no text is clipped, and no widget overlaps another — horizontal scrollbars appear only where necessary (inside table viewports, not on the page itself).

### Scenario 7 — Dashboard visual hierarchy

**Given** the Dashboard page is open  
**When** the user views the KPI card rows  
**Then** all cards in each row are the same height, equally spaced, and left/right edges align with the page content area.

---

## Functional Requirements

### FR-1: Action Button Visibility (All Tables)

- FR-1.1: Every table that contains an Actions column must size that column using a single fixed width pre-calculated to fit the widest button label that can appear in that column. For the Products table, the widest label is "Deactivate"; the column width is set once at build time, not recalculated per data load.
- FR-1.2: Buttons inside table cells must have a defined minimum width sufficient to display their full label text.
- FR-1.3: Buttons inside table cells must have consistent horizontal padding (minimum 8 px each side) and must not overflow the cell boundary.
- FR-1.4: When multiple buttons exist in the same Actions cell, they must be arranged with equal spacing and must not overlap.
- FR-1.5: At the minimum supported window width (900 px), when table columns cannot all fit simultaneously, a horizontal scrollbar appears on the table viewport only — the page itself never scrolls horizontally. The Actions column is always the last (rightmost) column; it scrolls into view and is never hidden or removed.

### FR-2: Table Layout Quality (All Tables)

- FR-2.1: All tables use a consistent row height across the application.
- FR-2.2: All table cells have consistent horizontal and vertical padding.
- FR-2.3: Column headers have consistent height, bold weight, and appropriate spacing.
- FR-2.4: Each table designates at least one column to stretch and fill available horizontal space, preventing unnecessary horizontal scrolling.
- FR-2.5: Fixed-width columns are sized to fit their longest expected content.
- FR-2.6: Tables do not display horizontal scrollbars unless the total column content genuinely exceeds the available width.
- FR-2.7: Text alignment within columns is consistent (left-aligned for text, right-aligned for numeric values).

### FR-3: Adaptive Table Height

- FR-3.1: Tables grow vertically as rows are added, up to a defined maximum height.
- FR-3.2: When a table reaches its maximum height, a vertical scrollbar appears inside the table viewport — the surrounding page does not scroll to accommodate the table.
- FR-3.3: When a table contains zero rows (hidden via empty-state label), or few rows, no large empty white container remains visible.
- FR-3.4: The minimum table height accommodates the header row plus at least one data row.

### FR-4: Reports Page Section Layout

- FR-4.1: Each of the six report sections (Sales History, Purchases History, Expenses History, Top Selling Products, Top Purchased Products, Top Expense Categories) follows the vertical structure: **Bold Section Title → Thin Separator Line → Search/Filter Controls → Table**.
- FR-4.2: Section titles are displayed as plain bold text at the standard heading size — not inside a GroupBox, heavy bordered frame, or oversized container.
- FR-4.3: The vertical spacing between the section title and the first control below it is consistent with the application's spacing scale.
- FR-4.4: Section panels in the horizontal splitter do not have excessive top/bottom padding around the title area.
- FR-4.5: The filter/summary card at the top of the Reports page remains visually distinct from the history panels below it.

### FR-5: Consistent Control Heights

- FR-5.1: A single standard control height (minimum 30 px) applies to all QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, and QDateTimeEdit controls across the application.
- FR-5.2: All QPushButton controls share one standard minimum height, equal to the standard control height.
- FR-5.3: When a search box, combo box, and button appear in the same horizontal row, all three sit on the same visual baseline.

### FR-6: Alignment & Spacing

- FR-6.1: On each page, the left edge of all major content areas (page titles, cards, tables, toolbars) aligns to a consistent left margin.
- FR-6.2: On each page, the right edge of all major content areas aligns to a consistent right margin.
- FR-6.3: The vertical gap between page sections (between title and first card, between cards, between table and footer) uses a consistent spacing value from the design-system spacing scale.
- FR-6.4: No two adjacent controls or containers use different margin/padding values unless intentionally differentiated by the design system.

### FR-7: Form Entry Pages (Sales, Purchases, Expenses)

- FR-7.1: The add-item row (Product selector + quantity field + price field where applicable + "Add" button) renders as a single horizontal toolbar with equal control heights and consistent spacing. The row is contained within a bordered card (QFrame with background and border) that visually separates the input area from the table below; the card border and background are preserved — only the internal layout is tightened.
- FR-7.2: The invoice header card (Invoice #, Date, Customer/Supplier) renders in compact form — no large blank areas inside the card.
- FR-7.3: The footer card (totals + action buttons) is vertically compact — it renders at the natural height of its content with no additional padding-induced inflation.
- FR-7.4: The page content (header card + add-item card + table + footer card) occupies only the vertical space needed; remaining window height is background, not blank white container.

### FR-8: Dashboard Layout

- FR-8.1: KPI cards in each row are equal height and equally spaced.
- FR-8.2: The left and right edges of the KPI card rows align with the edges of the Low Stock and Recent Transactions tables.
- FR-8.3: The Low Stock table and Recent Transactions table size naturally to their content (governed by FR-3).
- FR-8.4: Section dividers and spacing between Dashboard sections are consistent.

### FR-9: Products Page Layout

- FR-9.1: The search input and "Show Inactive" checkbox are vertically aligned to the same baseline as the "+ Add Product" button in the header row.
- FR-9.2: The product table uses available horizontal width efficiently — the Name column stretches; fixed columns are appropriately sized.
- FR-9.3: The Actions column uses a fixed width sized to the longest possible button set ("Edit" + "Deactivate"), set once at build time, so no row's buttons are ever clipped regardless of which combination appears in that row (FR-1.1 applies).
- FR-9.4: The empty page background below the table is unobtrusive (page background colour, not a white container).

### FR-10: Typography Consistency

- FR-10.1: Page titles use one consistent font size and weight.
- FR-10.2: Section headings use one consistent font size and weight, smaller than page titles.
- FR-10.3: Table column headers use bold weight.
- FR-10.4: Body/cell text uses the standard font size.
- FR-10.5: The spacing between a heading and the first element below it is consistent across pages.

### FR-11: Responsive Behaviour

- FR-11.1: At any window width between the minimum supported width and the maximum tested width (1280 px), no button is clipped or hidden.
- FR-11.2: Cards in grid layouts wrap or resize gracefully when horizontal space is reduced.
- FR-11.3: Horizontal scrollbars appear only inside table viewports (never on the main page). When a table cannot display all columns at the current window width, the table scrolls internally; the rightmost (Actions) column scrolls into view and is never clipped or hidden.
- FR-11.4: Vertical scrollbars on main pages appear only when total content height exceeds the window height.

### FR-12: Full Button Visibility Audit

- FR-12.1: Every interactive button on every page and dialog is fully visible (text not clipped, no overflow outside parent) at the default 1280×800 window size.
- FR-12.2: The audit covers: Dashboard, Products, Sales, Purchases, Expenses, Reports, Invoice Detail dialogs, Expense Detail dialogs, Product dialogs, Change Password dialog, Backup/Restore controls.

---

## Success Criteria

1. **Zero clipped buttons**: A full-screen review of all pages and dialogs at 1280×800 finds no button with clipped text, no button extending outside its container, and no button hidden by layout constraints.
2. **Consistent control height**: A visual inspection of any page containing mixed controls (search box + combo + button) confirms all controls appear at the same height.
3. **Adaptive tables**: After clearing all rows from any table, no empty white box taller than the header row + one row height remains visible. After adding 20 rows to any table, vertical scrolling activates inside the table viewport without pushing page content out of view.
4. **Reports page readability**: Each of the six report sections shows its title as plain bold text with no surrounding heavy frame; title-to-content spacing matches the application's spacing scale.
5. **Professional appearance**: A side-by-side comparison with a comparable screen from Manager.io or QuickBooks Desktop shows equivalent visual density, alignment, and polish.
6. **Window resize stability**: Resizing from 1280×800 to 900×600 produces no overlapping controls, no disappearing buttons, and no layout breakage on any page.
7. **Form page compactness**: On the Sales, Purchases, and Expenses pages with zero invoice lines, the form content (header + entry row + footer) occupies no more than 50% of a standard 800 px window height, with background showing below.

---

## Key Entities

| Entity | Description |
|--------|-------------|
| Page | One of: Dashboard, Products, Sales, Purchases, Expenses, Reports |
| Dialog | A modal window: Invoice Detail, Expense Detail, Product, Change Password |
| Table | A QTableWidget displaying tabular data on a page |
| Actions Column | The rightmost table column containing Edit/Delete/Deactivate/Activate buttons |
| Control | Any interactive widget: QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QPushButton |
| Card | A rounded-border surface grouping related fields (header info, footer totals) |
| Section Panel | A bordered panel inside the Reports page splitter holding a title, filters, and table |
| KPI Card | A fixed-size metric display card on the Dashboard |
| Spacing Scale | The design system's predefined spacing values (xs=4, sm=8, md=12, lg=16, xl=24, xxl=32) |

---

## Assumptions

1. The application runs on Windows 10+ at standard DPI (96 DPI). High-DPI scaling is out of scope for this feature.
2. The minimum supported window size is approximately 900×600 px.
3. The maximum tested window size is 1280×800 px (as used in current screenshots).
4. The design system's spacing scale and colour tokens remain unchanged.
5. The "standard control height" of 30 px (already set in the theme QSS) is the target for all input controls and buttons.
6. The existing `apply_table_style()` helper and `_fit_table_height()` mechanism in `theme.py` are the correct extension points for FR-3; this spec does not mandate replacing them.
7. Font sizes defined in `LightTheme` (`size_normal=10pt`, `size_heading=11pt`, `size_page_title=13pt`) are the correct typographic scale; this spec does not change font sizes.
8. The "maximum comfortable table height" referenced in FR-3.1 is the existing `_TABLE_MAX_HEIGHT` constant (390 px); changes to this value are an implementation detail.

---

## Dependencies

- `ui/theme.py` — Central QSS stylesheet, `apply_table_style()`, `_fit_table_height()`, spacing constants
- `ui/products_page.py` — Products table with Actions column
- `ui/sales_page.py` — Sales invoice entry form
- `ui/purchases_page.py` — Purchase invoice entry form
- `ui/expenses_page.py` — Expense invoice entry form
- `ui/reports_page.py` — Reports page with history and analytics sections
- `ui/dashboard_page.py` — Dashboard KPI cards and tables
- `ui/invoice_detail_dialog.py` — Sale/purchase detail modal
- `ui/expense_detail_dialog.py` — Expense detail modal
- `ui/product_dialog.py` — Product add/edit modal

---

## Constraints

- **No functional changes**: Business logic, database access, calculations, and workflows must remain identical.
- **Design token preservation**: Colours, font families, and spacing values defined in `LightTheme` must not be changed.
- **QSS compatibility**: All styling must remain compatible with PySide6's Qt Style Sheet engine on Windows.
- **No new dependencies**: No new Python packages or Qt modules may be introduced.
