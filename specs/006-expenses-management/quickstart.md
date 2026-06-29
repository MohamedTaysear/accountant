# Quickstart Validation Guide: Expenses Management

**Phase**: 6 — Expenses Management
**Date**: 2026-06-28

---

## Prerequisites

- Phase 5 (Dashboard & Reports) fully implemented and passing.
- Application launches without errors: `cd accounting_system && python main.py`
- Log in with the admin credentials.

---

## Section 1: Expenses Page — Basic CRUD

### 1.1 Add First Expense

1. Click **Expenses** in the sidebar.
2. Click **Add Expense**.
3. Verify the dialog opens with Date & Time defaulted to now.
4. Fill in:
   - Category: `Rent`
   - Description: `June office rent`
   - Amount: `1500`
   - Notes: *(leave blank)*
5. Click Save.

**Expected**: Dialog closes. Table shows one row: `EXP-000001`, current date/time, "Rent", "June office rent", "1,500.00", empty notes.

---

### 1.2 Validation — Required Fields

1. Click **Add Expense**.
2. Leave Category blank. Click Save.

**Expected**: Error dialog appears. Expense is NOT saved.

3. Fill Category = `Test`. Leave Description blank. Click Save.

**Expected**: Error dialog appears. Expense is NOT saved.

4. Fill Description = `test`. Set Amount to `0`. Click Save.

**Expected**: Error dialog appears. Expense is NOT saved.

---

### 1.3 Add More Expenses

Add the following expenses in order:

| Category | Description | Amount | Notes |
|----------|-------------|--------|-------|
| Electricity | May electricity bill | 250.50 | Building A |
| Salaries | Staff salaries June | 5000 | |
| Fuel | Delivery van fuel | 180 | |

**Expected**: Table shows EXP-000002, EXP-000003, EXP-000004 in order (most recent first = EXP-000004 at top).

---

### 1.4 Edit Expense

1. Click **Edit** on the Salaries row.
2. Change Amount to `5200`.
3. Click Save.

**Expected**: Table updates immediately; Salaries row shows `5,200.00`.

---

### 1.5 Delete Expense

1. Click **Delete** on the Fuel row.
2. Verify a confirmation dialog appears.
3. Click **Cancel**.

**Expected**: Fuel expense remains in table.

4. Click **Delete** on the Fuel row again. Click **Yes/OK** to confirm.

**Expected**: Fuel expense removed. Table has 3 rows.

---

## Section 2: Smart Category Autocomplete

1. Click **Add Expense**.
2. Click the Category field (do not type anything yet).

**Expected**: Dropdown shows suggestions: "Electricity", "Rent", "Salaries" (alphabetical, case-insensitive dedup).

3. Type `sal`.

**Expected**: Dropdown filters to show "Salaries".

4. Clear the field. Type `rent`.

**Expected**: Dropdown shows "Rent" (case-insensitive match).

5. Type `Packaging` (new category). Fill Description = `Packaging materials`, Amount = `90`. Save.

6. Click **Add Expense** again. Click Category field.

**Expected**: "Packaging" appears in the dropdown alongside Electricity, Rent, Salaries.

---

## Section 3: Search

1. On the Expenses page, type `EXP-000002` in the search box.

**Expected**: Only the Electricity row is shown.

2. Clear search. Type `sal`.

**Expected**: Only the Salaries row is shown.

3. Clear search. Type `Building`.

**Expected**: Only the Electricity row is shown (matches Notes).

4. Clear search.

**Expected**: All expenses restored.

---

## Section 4: Dashboard Updates

1. Click **Dashboard** in the sidebar.
2. Verify three new cards exist: "Today's Expenses", "This Month Expenses", "Net Profit".
3. Note the current values.

**Expected**:
- Today's Expenses = sum of expenses recorded today.
- This Month Expenses = sum of all expenses this calendar month.
- Net Profit = Total Profit (from sales) − Total Expenses (all-time).

4. Navigate to Expenses. Add a new expense: Category = `Cleaning Supplies`, Amount = `75`.
5. Navigate back to Dashboard.

**Expected**: Today's Expenses and This Month Expenses increased by 75. Net Profit decreased by 75.

6. Verify that "Today's Profit", "This Month Profit", and "Total Profit" are **unchanged** compared to before the expense was added.

---

## Section 5: Expenses Report

1. Click **Expenses Report** in the sidebar.
2. Verify the page loads with the expenses table populated (default filter = Today or This Month).

### 5.1 Date Filter

1. Select "This Month" from the date filter combo.

**Expected**: Only expenses from this calendar month are shown.

2. Select "Custom Range". Set From = first day of current month, To = today. Click Apply.

**Expected**: Same results as "This Month".

### 5.2 Category Filter

1. Select "Rent" from the category filter.

**Expected**: Only the Rent expense is shown.

2. Select "All Categories".

**Expected**: All expenses shown.

### 5.3 Search

1. Type `office` in the search box.

**Expected**: Only the Rent expense ("June office rent") is shown.

2. Clear search.

### 5.4 Expense Detail Dialog

1. Double-click any expense row.

**Expected**: Expense Detail dialog opens showing all fields (read-only): Expense Number, Date & Time, Category, Description, Amount, Notes, Created At.

2. Close the dialog.

### 5.5 CSV Export

1. Apply no filters (show all). Click **Export to CSV**.
2. Choose a save path and confirm.

**Expected**: File saved. Open the CSV and verify:
- Headers: Expense #, Date & Time, Category, Description, Amount, Notes.
- Rows match all visible expenses exactly.

3. Apply category filter = "Rent". Click **Export to CSV**.

**Expected**: CSV contains only the Rent expense row.

---

## Section 6: Restart Persistence

1. Close the application completely.
2. Relaunch: `python main.py`. Log in.
3. Navigate to Expenses.

**Expected**: All expenses from previous session still present with correct data.

4. Check category suggestions: open Add Expense dialog, click Category.

**Expected**: All previously used categories still appear as suggestions.

5. Navigate to Dashboard and verify expense KPI values are correct.

---

## Section 7: Regression — Previous Phases

Run these checks to confirm no regressions:

- [ ] Products page: add/edit/delete/search still works.
- [ ] Sales page: create and void a sale; stock updates correctly.
- [ ] Purchases page: create and void a purchase; stock updates correctly.
- [ ] Reports page: Sales History and Purchases History load correctly with date filters.
- [ ] Dashboard: Today's Profit, This Month Profit, Total Profit values are unchanged by expense operations.
- [ ] `SaleItems.purchase_price_at_sale` values: verify existing sales still display correct profit in Invoice Detail dialog.

---

## Pass Criteria

All scenarios above must pass without errors, crashes, or data loss before Phase 6 is considered complete.
