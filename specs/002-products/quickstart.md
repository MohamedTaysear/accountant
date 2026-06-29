# Quickstart & Validation Guide: Product Catalog Management

**Feature**: 002-products
**Date**: 2026-06-27
**Purpose**: Manual testing guide for verifying Phase 2 is complete before Phase 3
begins. Every checkpoint below MUST pass in a single continuous session. Phase 1
checkpoints must also remain fully working (regression check).

---

## Prerequisites

- Phase 1 fully implemented and all Phase 1 checkpoints passing.
- All three Phase 2 files implemented: `products_db.py`, `ui/product_dialog.py`,
  `ui/products_page.py` (replacing the placeholder).
- Run from `accounting_system/`:

```
python main.py
```

Log in with Admin credentials and navigate to the **Products** page via the sidebar.

---

## Checkpoint 1 — Add a Product (All Fields)

Steps:
1. Click "Add Product".
2. Fill in: Name = "Laptop", SKU = "LAP-001", Unit = "pcs", Purchase Price = 800,
   Selling Price = 1200, Stock Quantity = 10, Reorder Level = 3.
3. Click Save.

Expected:
- Dialog closes.
- "Laptop" appears in the product table immediately with all values correct.
- Status shows "Active".

---

## Checkpoint 2 — Add a Product (Minimal — Name Only)

Steps:
1. Click "Add Product".
2. Fill in Name = "Generic Item", leave all other fields at defaults.
3. Click Save.

Expected:
- Product saved with Unit = "pcs", prices = 0, stock = 0, reorder = 5.
- Appears in table immediately.

---

## Checkpoint 3 — Add a Product with Decimal Quantities

Steps:
1. Click "Add Product".
2. Fill in Name = "Sugar", Unit = "kg", Stock Quantity = 12.5, Reorder Level = 2.0,
   Purchase Price = 1.5, Selling Price = 2.0.
3. Click Save.

Expected:
- "Sugar" appears in table with Stock Quantity = 12.5 and Reorder Level = 2.0.

---

## Checkpoint 4 — Duplicate SKU is Rejected

Steps:
1. Click "Add Product".
2. Fill in Name = "Another Laptop", SKU = "LAP-001" (same as Checkpoint 1).
3. Click Save.

Expected:
- A friendly error message appears: "SKU already in use…" (or similar).
- Dialog stays open.
- No new product is added to the table.

---

## Checkpoint 5 — Validation: Empty Name

Steps:
1. Click "Add Product".
2. Leave Name blank, fill in a price.
3. Click Save.

Expected:
- Error message about name being required.
- Dialog stays open.

---

## Checkpoint 6 — Validation: Negative Price

Steps:
1. Click "Add Product".
2. Fill in Name = "Test", Purchase Price = -5.
3. Click Save.

Expected:
- Error message about price being 0 or greater.
- Dialog stays open.

---

## Checkpoint 7 — Selling Price Below Purchase Price (Warning, Not Block)

Steps:
1. Click "Add Product".
2. Fill in Name = "Clearance Item", Purchase Price = 100, Selling Price = 80.
3. Click Save.

Expected:
- A warning dialog appears asking "Selling price is less than purchase price. Save
  anyway?" with Yes and No buttons.
- Clicking Yes: product saves successfully.
- Clicking No: dialog stays open, no save.

---

## Checkpoint 8 — Edit a Product

Steps:
1. Click Edit on the "Laptop" row.
2. Change Selling Price from 1200 to 1350 and Reorder Level from 3 to 5.
3. Click Save.

Expected:
- Dialog closes.
- Table shows updated values (1350, 5) for Laptop immediately.

---

## Checkpoint 9 — Edit: Cancel Makes No Changes

Steps:
1. Click Edit on any product.
2. Change a value.
3. Click Cancel.

Expected:
- Dialog closes.
- Original values are unchanged in the table.

---

## Checkpoint 10 — Delete an Unused Product

Steps:
1. Identify a product that has never been used in any invoice (all products at this
   point in Phase 2 qualify).
2. Click Delete on "Generic Item".
3. Confirm in the confirmation dialog.

Expected:
- "Generic Item" is permanently removed from the table.
- No error.

---

## Checkpoint 11 — Cancel Delete

Steps:
1. Click Delete on any product.
2. Click Cancel in the confirmation dialog.

Expected:
- Product remains in the table unchanged.

---

## Checkpoint 12 — Search by Name

Steps:
1. In the search box, type "lap" (partial name match).

Expected:
- Only "Laptop" (and any other products whose name contains "lap") remains visible.
- Other products are hidden while search text is present.

---

## Checkpoint 13 — Search by SKU

Steps:
1. Clear any existing search text.
2. Type "LAP" in the search box.

Expected:
- Only products with a SKU containing "LAP" are shown (case-insensitive).

---

## Checkpoint 14 — Clear Search Restores Full List

Steps:
1. With a search active, clear the search box.

Expected:
- All active products reappear in the table.

---

## Checkpoint 15 — Show Inactive Toggle

Steps:
1. (After Phase 3 introduces invoice data, the Deactivate path can be fully tested.
   For Phase 2, verify the checkbox mechanism itself.)
2. Check "Show Inactive" checkbox.
3. Uncheck "Show Inactive" checkbox.

Expected:
- Checking: table reloads; if any inactive products exist, they appear; a Status
  column or indicator distinguishes them.
- Unchecking: inactive products disappear from the list again.

---

## Checkpoint 16 — Changes Persist After App Restart

Steps:
1. Close the application.
2. Relaunch `python main.py`.
3. Navigate to Products page.

Expected:
- All products added/edited in this session are still present with correct values.
- Deleted product is gone.

---

## Checkpoint 17 — Phase 1 Regression Check

Steps:
1. Navigate to Dashboard, Sales, Purchases, Reports pages via sidebar → no crash.
2. Backup Now → creates a backup file.
3. Change Password → still works.
4. Logout → returns to Login Window.

Expected:
- All Phase 1 features work identically to before Phase 2 was implemented.

---

## Exit Criteria

All 17 checkpoints above MUST pass before Phase 3 (Purchases) work begins. Any
failure is a blocker.
