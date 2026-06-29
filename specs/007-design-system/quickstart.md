# Quickstart: Design System & UI Modernization — Validation Guide

## Prerequisites

- The application is fully functional per all prior phases (Phases 1–6).
- The design system implementation is complete (`ui/theme.py` exists, all UI files updated, global stylesheet applied in `main.py`).
- Run the application: `python main.py` from `accounting_system/`.

---

## Section 1 — Startup & Global Stylesheet

**Scenario**: Verify the global QSS applies at startup.

1. Launch the application. The Login Window appears.
2. **Check**: Background is near-white (`#F1F5F9`), not OS-default gray.
3. **Check**: Username and Password fields have a visible border and consistent padding.
4. **Check**: The Login button uses the Primary style (blue background, white text).
5. **Check**: No Python warnings or errors in the console regarding stylesheet syntax.

**Pass criteria**: Login window is visibly styled; no console errors.

---

## Section 2 — Navigation Sidebar

**Scenario**: Verify sidebar styling and navigation icon consistency.

1. Log in with valid credentials. The Main Window opens on the Dashboard.
2. **Check**: Sidebar background is dark (`#1E293B`), not OS-default.
3. **Check**: Nav buttons (Dashboard, Products, Sales, Purchases, Expenses, Reports) have consistent text color and padding.
4. **Check**: Each nav button displays an icon to the left of its label.
5. **Check**: The active page's nav button has a visible left accent bar and/or distinct highlight.
6. Click each nav button in turn. **Check**: The active button state updates correctly on each click.

**Pass criteria**: Sidebar is consistently styled; all icons present; active state visible.

---

## Section 3 — Dashboard KPI Cards

**Scenario**: Verify all KPI cards share identical visual design.

1. Navigate to the Dashboard.
2. **Check**: All KPI cards have the same padding, border radius, and white background.
3. **Check**: All cards have a subtle drop shadow.
4. **Check**: KPI numeric values are large and bold (≈18pt).
5. **Check**: Profit-related values (Today's Profit, Net Profit, This Month Profit) appear in green (`#16A34A`) when positive.
6. If any profit value is negative (more purchases than sales), **check** that it appears in red (`#DC2626`).
7. **Check**: All card label texts are small and use secondary text color.
8. **Check**: Cards appear visually balanced — no card noticeably larger or smaller than others at the same window size.
9. **Check**: Low Stock table (if visible) uses the standard table style — alternating rows, consistent header.

**Pass criteria**: All cards visually identical in structure; profit values correctly color-coded.

---

## Section 4 — Tables Across All Screens

**Scenario**: Verify table visual consistency across the entire application.

Run these checks on: Products table, Sales in-progress items table, Purchases in-progress items table, Expenses in-progress items table, Reports Sales history, Reports Purchases history, Reports Expenses history.

For each table:

1. **Check**: Header row is bold, has a distinct background, and a bottom border.
2. **Check**: Row height is consistent (≈28px) — no tall or short rows.
3. **Check**: Rows alternate between white and very light gray.
4. **Check**: Clicking a row highlights it in a light blue selection color.
5. **Check**: Grid lines are visible between cells and columns.
6. Add a product/record with a very long name (e.g., 60+ characters). **Check**: The text truncates with an ellipsis (…) in the cell.
7. Hover over the truncated cell. **Check**: A tooltip appears showing the full text.

**Pass criteria**: All tables look identical; truncation and tooltip confirmed.

---

## Section 5 — Empty State Messages

**Scenario**: Verify both distinct empty-state messages appear correctly.

**Empty data (no records exist)**:
1. If the Products table is empty, navigate to Products. **Check**: A centered message like "No products added yet." appears — the table area is not blank.
2. If the Sales history table is empty (Reports page), **check** a similar "no records" message.

**Empty search results**:
1. Navigate to the Products page (with at least one product).
2. Type a search term that matches nothing. **Check**: The table is replaced by "No results match your search." (not "No products added yet.").
3. Clear the search. **Check**: Products reappear; message is hidden.

**Pass criteria**: Both distinct messages confirmed; transitions between states work correctly.

---

## Section 6 — Buttons and Interactive Controls

**Scenario**: Verify button and input consistency across screens.

1. Compare the "Save Invoice" button on the Sales page, Purchases page, and Expenses page. **Check**: All three buttons are visually identical (same color, size, padding, border radius).
2. Compare the "Delete" button (Products page) and "Void" button (Invoice Detail Dialog). **Check**: Both use the destructive style (red background, white text).
3. Compare "Clear Invoice" buttons across Sales, Purchases, Expenses. **Check**: Visually identical.
4. Click into a QLineEdit input on any form. **Check**: The border changes to a blue focus ring (`#93C5FD`).
5. Click into a QComboBox. **Check**: Same focus ring behavior.
6. Tab through form fields. **Check**: Focus indicator is clearly visible on every focused control.

**Pass criteria**: Save buttons identical; destructive buttons identical; focus indicators visible.

---

## Section 7 — Dialogs

**Scenario**: Verify dialog consistency.

1. Open the Invoice Detail Dialog (double-click a saved invoice in Reports). **Check**: White background, consistent padding, line-items table uses standard table style.
2. Open the Change Password dialog. **Check**: Same visual treatment as Invoice Detail Dialog.
3. Trigger a confirmation dialog (delete a product). **Check**: Consistent button placement (e.g., Yes/No or OK/Cancel) with correct styling.
4. **Check**: All dialogs have consistent spacing between form rows.

**Pass criteria**: All dialogs visually consistent; tables inside dialogs use standard style.

---

## Section 8 — Full Regression Pass

**Scenario**: Verify all existing functionality works after design system application.

Run through each of these operations and confirm they work exactly as before:

- [ ] Log in / log out
- [ ] Add, edit, and delete a product
- [ ] Deactivate and reactivate a product
- [ ] Search products by name
- [ ] Create a multi-line purchase invoice and save it
- [ ] Create a multi-line sales invoice and save it
- [ ] Create a multi-line expense invoice and save it
- [ ] Clear an in-progress invoice (with confirmation)
- [ ] View Reports with date filter changes
- [ ] Double-click a Sales invoice → Invoice Detail Dialog opens correctly
- [ ] Double-click a Purchase invoice → Invoice Detail Dialog opens correctly
- [ ] Double-click an Expense invoice → Expense Detail Dialog opens correctly
- [ ] Void a Sales invoice
- [ ] Export Reports to CSV
- [ ] Create a database backup (Backup menu → Create Backup)
- [ ] Change password and log back in with the new password
- [ ] Resize the main window — no layout breaks; minimum size is enforced

**Pass criteria**: All operations function identically to before the design system was applied. Zero regressions.

---

## Pass/Fail Summary

| Section | Description | Pass? |
|---|---|---|
| 1 | Startup & global stylesheet | |
| 2 | Navigation sidebar | |
| 3 | Dashboard KPI cards | |
| 4 | Tables (all screens) | |
| 5 | Empty state messages | |
| 6 | Buttons and controls | |
| 7 | Dialogs | |
| 8 | Full regression pass | |

All sections must pass before this phase is considered complete.
