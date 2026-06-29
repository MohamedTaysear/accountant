Before starting the current Final Polish phase, I would like to introduce one additional functional phase.

This is a core accounting feature and should be implemented before Final Polish.

Please update the Blueprint, Specification, Plan, Tasks, and Quickstart accordingly before implementation.

The project phases should become:

* Phase 1 – Authentication
* Phase 2 – Products
* Phase 3 – Purchases
* Phase 4 – Sales
* Phase 5 – Dashboard & Reports
* **Phase 6 – Expenses Management**
* **Phase 7 – Final Polish**

---

# Phase 6 — Expenses Management

## Goal

Implement a complete Expenses Management module.

Expenses are independent from Purchases.

Purchases increase inventory assets.

Expenses represent operating/business costs.

---

# Database

Create a dedicated `Expenses` table.

Suggested fields:

* id
* expense_number (EXP-000001...)
* expense_datetime
* category
* description
* amount
* notes (optional)
* created_at

Do not reuse Purchases tables.

No unnecessary schema changes outside the new Expenses module.

---

# Expenses Page

Add a new page in the sidebar called **Expenses**.

The page should follow the same architecture and visual style as the existing pages.

Display:

* Search box
* Add Expense button
* Expenses table

Table columns:

* Expense Number
* Date & Time
* Category
* Description
* Amount
* Notes
* Actions (Edit / Delete)

---

# Expense Dialog

The Add/Edit Expense dialog should contain:

* Date & Time (default = current date/time)
* Category
* Description
* Amount
* Notes (optional)

Validation:

* Category is required.
* Description is required.
* Amount must be greater than zero.
* Notes are optional.

---

# Smart Category Field

The Category field must behave exactly like the Product Category field.

Requirements:

* Use an editable ComboBox.
* Show previously used expense categories automatically.
* Allow selecting an existing category.
* Allow typing a completely new category.
* When a new category is saved for the first time, it becomes available automatically in future expenses.
* No separate Category Management screen is required.

Example:

Existing categories:

* Rent
* Electricity
* Salaries

User may type:

* Fuel
* Packaging
* Cleaning Supplies

After saving, these categories automatically appear in the dropdown for future expenses.

---

# Search

Search should work by:

* Expense Number
* Category
* Description
* Notes

---

# Dashboard Integration

Add the following new Dashboard cards:

* Today's Expenses
* This Month Expenses
* Net Profit

Definitions:

Today's Expenses

= Total operating expenses recorded today.

This Month Expenses

= Total operating expenses recorded during the current calendar month.

Net Profit

= Total Profit − Total Expenses

Where:

Total Profit continues to represent cumulative sales profit only and MUST continue using the historical purchase cost stored in `SaleItems.purchase_price_at_sale`.

Net Profit is a separate KPI representing the actual business profit after operating expenses.

Do NOT change the meaning of the existing:

* Today's Profit
* This Month Profit
* Total Profit

These continue to represent sales profit only.

All Dashboard cards must refresh automatically whenever an expense is added, edited, or deleted.

---

# Reports

Add an Expenses History report.

Support:

* Date filtering
* Category filtering
* Search
* Expense Detail dialog
* CSV Export

The report must follow the same UI and behavior as Sales and Purchases History.

---

# Expense Number

Expense numbers should follow the existing numbering convention.

Examples:

EXP-000001

EXP-000002

EXP-000003

---

# Date & Time

Every expense must store the exact creation date and time.

Display both date and time consistently throughout the application, including:

* Expenses page
* Reports
* Expense Detail dialog
* Printed reports (if applicable)

---

# Architecture

Maintain the existing architecture:

UI
→ Logic
→ Database

No SQL inside UI files.

Business rules belong in the Logic layer.

---

# Compatibility

Do not break any existing functionality.

Historical sales profit calculations must continue using `SaleItems.purchase_price_at_sale`.

No existing reports or dashboard calculations should regress.

---

# Manual Testing

Create a complete Quickstart Validation Guide for the Expenses phase covering:

* Add Expense
* Edit Expense
* Delete Expense
* Search
* Smart Category suggestions
* Dashboard updates
* Today's Expenses
* This Month Expenses
* Net Profit
* Reports
* CSV Export
* Date filters
* Restart persistence
* Regression with previous phases

The Expenses phase should not be considered complete until every validation scenario passes successfully.

After Phase 6 is completed, continue with the existing Final Polish phase (renumbered to Phase 7).
