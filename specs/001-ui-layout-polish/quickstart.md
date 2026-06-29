# Quickstart Validation Guide: UI Layout Polish

**Date**: 2026-06-29 | **Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Prerequisites

- Python environment with PySide6 installed
- At least one product, one sale invoice, one purchase invoice, and one expense invoice in the database (to populate tables with real data)
- Application running at 1280x800 (default launch size)

## Launch

```
cd accounting_system
python main.py
```

Log in with the admin credentials, then follow the validation scenarios below page by page.

---

## Scenario 1 — Products Page: Action Buttons Visible (FR-1, FR-9)

1. Navigate to **Products**.
2. With at least one product listed, inspect the Actions column.
   - **Pass**: Both buttons (Edit + Delete or Edit + Deactivate) fully visible, no text clipped, no button cut off at the cell boundary.
   - **Fail**: Any button text is clipped, button extends outside the cell, or buttons overlap.
3. Enable "Show Inactive" to toggle between active/inactive products.
   - **Pass**: The "Activate" button (which replaces "Deactivate") is also fully visible with no layout shift in the column width.
4. Resize window to 900x600.
   - **Pass**: A horizontal scrollbar appears inside the table viewport (not on the page). Scrolling right reveals the Actions column; buttons remain fully visible.
   - **Fail**: Actions column disappears or buttons are cropped at 900 px width.

---

## Scenario 2 — Products Page: Header Row Alignment (FR-9.1)

1. On the Products page, examine the top toolbar row (search input + "Show Inactive" checkbox + "+ Add Product" button).
   - **Pass**: All three controls share the same visual height and are vertically centred on the same baseline.
   - **Fail**: Any control appears taller or shorter than the others, or sits higher/lower than the row baseline.

---

## Scenario 3 — Adaptive Table Height (FR-3)

1. On the **Products** page with 0 active products (hide all or deactivate all):
   - **Pass**: No large white empty table area — the empty-state label shows instead; the table widget is hidden.
2. Add one product; navigate back to Products.
   - **Pass**: Table height matches approximately 1 header row + 1 data row; no large empty area below the single row.
3. Add 20+ products and navigate back.
   - **Pass**: Table grows to maximum height (~390 px / ~12 rows) and a vertical scrollbar appears inside the table viewport. Page layout below the table remains stable (not pushed down).

---

## Scenario 4 — Sales Page: Add-Item Row (FR-7.1)

1. Navigate to **Sales** > New Sale Invoice.
2. Examine the add-item card: Product combo, Qty spinbox, and "+ Add to Invoice" button.
   - **Pass**: All three controls appear at the same visual height, are vertically centred, and have consistent spacing between them.
3. With zero lines in the invoice, the page form (header card + add-item card + footer card) should occupy no more than 50% of the visible window height.
   - **Pass**: Substantial background colour visible below the footer card.
   - **Fail**: Footer card stretches to the bottom of the window or there is a large white container filling the page.

Repeat steps 1-3 for **Purchases** and **Expenses** pages.

---

## Scenario 5 — Reports Page: Section Layout (FR-4)

1. Navigate to **Reports**.
2. Examine the six history/analytics panels.
   - **Pass**: Each panel shows: Bold section title (e.g., "Sales History") → thin separator line → search/filter controls → table. No heavy bordered frame surrounds the title.
   - **Fail**: Section title is inside a prominent GroupBox-style frame, or there is large empty space between the title and the first control.

---

## Scenario 6 — Consistent Control Heights (FR-5)

1. On the **Products** page, the search input and "+ Add Product" button should be the same height (30 px).
2. On the **Reports** page, the category combo and date filter should be the same height as the search button.
   - **Pass**: All controls appear at identical visual height in any mixed-control row.
   - **Fail**: Any control is visually taller or shorter than its row neighbours.

---

## Scenario 7 — Dialog Button Visibility (FR-12)

1. From the Products page, open the **Add Product** dialog.
   - **Pass**: "Save" and "Cancel" buttons fully visible, no text clipped.
2. From the Sales History (Reports or invoice list), open an **Invoice Detail** dialog.
   - **Pass**: "Void Invoice" (or disabled equivalent) and "Close" buttons fully visible.
3. From the main window menu, open **Change Password**.
   - **Pass**: "Change Password" and "Cancel" buttons fully visible.
4. From the Expenses History, open an **Expense Detail** dialog.
   - **Pass**: All buttons visible.

---

## Scenario 8 — Window Resize Stability (FR-11)

1. With the application at 1280x800, resize to 900x600.
   - **Pass**: No button disappears, no text is clipped, no widget overlaps another. Table viewports show horizontal scrollbars where needed; the page itself does not scroll horizontally.
2. Resize back to 1280x800.
   - **Pass**: Layout returns to normal with no residual clipping or misalignment.

---

## Pass / Fail Summary

| Scenario | Requirement | Status |
|----------|-------------|--------|
| 1 — Products Actions buttons | FR-1, FR-9.3, SC-1 | |
| 2 — Products header alignment | FR-9.1, SC-2 | |
| 3 — Adaptive table height | FR-3, SC-3 | |
| 4 — Form page add-item row | FR-7.1, SC-7 | |
| 5 — Reports section layout | FR-4, SC-4 | |
| 6 — Consistent control heights | FR-5, SC-2 | |
| 7 — Dialog button visibility | FR-12, SC-1 | |
| 8 — Window resize stability | FR-11, SC-6 | |

All scenarios must pass before the feature is considered complete.
