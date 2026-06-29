UI Layout Review & Refinement

You already have the latest screenshots of the application.

Please review every screen carefully before making changes.

The design system is mostly implemented, but the UI still has several layout and usability problems.

This task is UI layout refinement only.

Do NOT change any business logic, database logic, calculations, workflows, or navigation.

1. Fix Action Buttons Inside Tables

The biggest issue is the Actions column.

Currently the Edit/Delete buttons are either:

invisible,
clipped,
partially hidden,
or extend outside their cells.

This makes the Actions column unusable.

Requirements
Every action button must be fully visible.
Buttons must fit completely inside the table cell.
Use proper padding.
Use consistent button sizes.
The Actions column width should automatically fit its contents.
Never crop buttons.
Never overlap buttons.
Never allow buttons to exceed the cell boundaries.
2. Improve Table Layout

Many tables still feel poorly designed.

Improve every table in the application.

Requirements:

Better row height.
Better cell padding.
Better header spacing.
Better column spacing.
Proper text alignment.
Consistent header height.
Automatic column sizing where appropriate.
Stretch the correct columns.
Prevent unnecessary horizontal scrolling.

Tables should resemble professional desktop accounting software.

3. Remove Fixed Heights

Many sections still use fixed heights.

Instead:

use adaptive layouts,
allow widgets to size naturally,
use proper QSizePolicy,
use layouts instead of fixed geometry.

Avoid huge empty containers.

4. Reports Page

The Reports page still looks like multiple unrelated boxes.

Redesign the layout.

Each report section should be:

Section Title

↓

Search / Filters

↓

Table

Titles should not sit inside oversized framed containers.

Remove unnecessary decorative frames.

Spacing between sections should be consistent.

5. Consistent Control Heights

Many controls have different heights.

Examples:

Search boxes
Combo boxes
Line edits
Spin boxes
Buttons

Standardize them.

All input controls should share one visual height.

Buttons should also follow one standard height.

6. Improve Alignment

Many widgets are misaligned.

Requirements:

Align left edges.
Align right edges.
Equal spacing.
Equal margins.
Consistent padding.
Consistent vertical rhythm.

Everything should appear placed on a design grid.

7. Purchases / Sales / Expenses Pages

The forms still have spacing problems.

Examples include:

Qty field
Unit Price field
Product selector
Total label
Buttons

These controls should feel like a single toolbar.

They should have:

equal heights,
equal spacing,
proper alignment,
no oversized empty areas.
8. Dashboard

Improve visual hierarchy.

Requirements:

KPI cards aligned perfectly.
Equal spacing between cards.
Better spacing before tables.
Low Stock table should size naturally.
Recent Activity should align perfectly with the section above.
9. Products Page

The Products page still has layout issues.

Requirements:

Search area should align perfectly with the Add Product button.
Table should use available width efficiently.
Action buttons should be fully visible.
Empty space below the table should be minimized.
10. Typography

Improve typography consistency.

Requirements:

Consistent font sizes.
Proper heading hierarchy.
Table headers slightly bolder.
Labels easier to read.
Better spacing between headings and content.
11. Responsive Layout

When resizing the window:

Tables resize correctly.
Cards remain aligned.
Controls never overlap.
Buttons never disappear.
Columns resize appropriately.
No clipped widgets.
No excessive whitespace.
12. Layout Implementation

If necessary:

Replace existing layouts.
Replace container hierarchy.
Replace fixed geometry.
Replace fixed sizes.

You are allowed to redesign the layout structure completely.

Do NOT keep a poor layout just to preserve existing code.

13. Before Writing Code

For each page:

Identify every layout issue you found.
Explain how you will fix it.
Then implement the improved layout.

Do not simply adjust colors or stylesheets.

Focus on proper desktop UI layout.
14. Ensure Every Button Is Fully Visible

Across the entire application, every button must always be fully visible.

Currently, several buttons are:

partially clipped,
hidden inside table cells,
cut off by layouts,
overlapped by neighboring widgets,
or too small to display their text.

This is not acceptable.

Requirements
Every button must always be fully visible.
Button text must never be clipped.
Icons (if present) must always be fully visible.
Buttons must never overlap other controls.
Buttons must never extend outside their parent container.
Buttons must never be cropped by layouts.
Buttons must keep consistent padding.
Buttons must have a reasonable minimum width based on their content.
Table action buttons must fit entirely inside the Actions column.
The Actions column must automatically reserve enough width for all buttons.
Buttons should remain fully visible at all supported window sizes.
No button anywhere in the application should disappear because of layout constraints.

Review every page, including:

Dashboard
Products
Sales
Purchases
Expenses
Reports
Dialogs
Popups
Backup / Restore
Change Password

Verify that every single button is completely visible and usable.

Final Validation

Before considering this task complete, perform a full UI review and verify that:

No button is clipped.
No text is clipped.
No icon is clipped.
No table column hides buttons.
No control overlaps another control.
No layout causes widgets to disappear.
Every page remains fully usable at different window sizes.

Do not consider the implementation finished until every button in the application is fully visible and accessible.

Final Goal

The final application should look comparable to professional desktop accounting software such as:

Manager.io
QuickBooks Desktop
Odoo Desktop
ERPNext Desktop

The emphasis should be on:

Professional layout
Visual balance
Consistent spacing
Adaptive tables
Clean alignment
Fully visible controls
No clipped buttons
No oversized empty containers
High usability

Do not stop after fixing one page. Apply these improvements consistently across the entire application.