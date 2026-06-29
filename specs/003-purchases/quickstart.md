# Quickstart & Validation Guide: Purchase Invoice Management

**Feature**: 003-purchases
**Date**: 2026-06-27
**Purpose**: Manual testing guide for verifying Phase 3 is complete before Phase 4
begins. Every checkpoint below MUST pass in a single continuous session. Phase 1 and
Phase 2 checkpoints must also remain fully working (regression check).

---

## Prerequisites

- Phase 1 and Phase 2 fully implemented and all prior checkpoints passing.
- At least three active products exist in the catalog (add them in Products page if not):
  - **Laptop** — Purchase Price: 800, Stock: 0
  - **Mouse** — Purchase Price: 15, Stock: 0
  - **Sugar** (unit: kg) — Purchase Price: 1.5, Stock: 0
- All three Phase 3 files implemented:
  `purchases_db.py`, `logic/purchase_logic.py`, `ui/purchases_page.py`
- Run from `accounting_system/`:

```
python main.py
```

Log in and navigate to the **Purchases** page via the sidebar.

---

## Checkpoint 1 — Page Loads with Auto-Generated Invoice Number

Steps:
1. Navigate to Purchases page.

Expected:
- Invoice number field shows `PUR-000001` (read-only; not editable).
- Date field shows today's date (read-only).
- Supplier Name field is blank.
- Line-items table is empty.
- Total displays 0.00.

---

## Checkpoint 2 — Add a Line Item

Steps:
1. Select "Laptop" from the product picker.
2. Confirm focus jumps to the Quantity field automatically.
3. Enter Quantity: 5, Unit Price: 850.
4. Click "Add to Invoice".

Expected:
- A row appears in the line-items table: Laptop | 5 | 850.00 | 4,250.00
- Running Total updates to 4,250.00.
- Focus returns automatically to the product picker.

---

## Checkpoint 3 — Add a Second Line Item (Decimal Quantity)

Steps:
1. Select "Sugar" from the product picker.
2. Enter Quantity: 12.5, Unit Price: 2.00.
3. Click "Add to Invoice".

Expected:
- Second row: Sugar | 12.5 | 2.00 | 25.00
- Running Total updates to 4,275.00.

---

## Checkpoint 4 — Validation: Zero Quantity Rejected

Steps:
1. Select "Mouse" from the product picker.
2. Enter Quantity: 0, Unit Price: 20.
3. Click "Add to Invoice".

Expected:
- Error message: "Quantity must be greater than 0." (or similar).
- No row added to the table; running total unchanged.

---

## Checkpoint 5 — Validation: Negative Unit Price Rejected

Steps:
1. Select "Mouse" from the product picker.
2. Enter Quantity: 2, Unit Price: -5.
3. Click "Add to Invoice".

Expected:
- Error message about unit price being invalid.
- No row added.

---

## Checkpoint 6 — Zero Unit Price is Accepted

Steps:
1. Select "Mouse" from the product picker.
2. Enter Quantity: 3, Unit Price: 0.
3. Click "Add to Invoice".

Expected:
- Row added: Mouse | 3 | 0.00 | 0.00
- Running total unchanged (still 4,275.00).

---

## Checkpoint 7 — Remove a Line Item

Steps:
1. Remove the Mouse row (click its Remove/Delete button).

Expected:
- Mouse row disappears from table.
- Running total returns to 4,275.00.

---

## Checkpoint 8 — Optional Supplier Name

Steps:
1. Enter "Tech Supplies Co." in the Supplier Name field.

Expected:
- Field accepts the text with no validation errors.

---

## Checkpoint 9 — Clear Invoice (with lines present — requires confirmation)

Steps:
1. Click "Clear Invoice" while Laptop and Sugar lines exist.

Expected:
- Confirmation dialog appears: "Are you sure you want to clear this invoice?" (or similar).
- Click **Cancel**: form is unchanged, lines are still present.
- Click **Clear Invoice** (or Yes): form resets — lines gone, supplier name blank,
  total back to 0.00, invoice number still shows PUR-000001.

---

## Checkpoint 10 — Clear Invoice (no lines — no confirmation)

Steps:
1. With an empty line-items table, click "Clear Invoice".

Expected:
- Form resets immediately — no confirmation dialog appears.

---

## Checkpoint 11 — Save Blocked with Zero Line Items

Steps:
1. Ensure the line-items table is empty.
2. Click "Save Invoice".

Expected:
- Error message: "Invoice must have at least one item" (or similar).
- No database write occurs.

---

## Checkpoint 12 — Successful Multi-Line Purchase Save

Steps:
1. Add two products: Laptop (qty 5, price 850) and Sugar (qty 12.5, price 2.00).
2. Enter Supplier Name: "Tech Supplies Co."
3. Click "Save Invoice".

Expected:
- Wait cursor briefly appears during save.
- Success message or silent success — form resets to initial state.
- Invoice number resets to `PUR-000002`.
- Line-items table is empty. Running total shows 0.00. Supplier name is blank.

---

## Checkpoint 13 — Stock Quantities Updated

Steps:
1. Navigate to the **Products** page.

Expected:
- Laptop: Stock Quantity = 5.00 (was 0, increased by 5)
- Sugar: Stock Quantity = 12.50 (was 0, increased by 12.5)
- Mouse: Stock Quantity = 0.00 (unchanged — we cleared/didn't save)

---

## Checkpoint 14 — Purchase Price Updated

Steps:
1. On Products page, click Edit on Laptop.

Expected:
- Purchase Price field shows 850.00 (updated from 800 when we saved the invoice).

---

## Checkpoint 15 — Invoice Number Increments Correctly

Steps:
1. Navigate back to Purchases page.
2. Add one line item (any product).
3. Save the invoice.

Expected:
- Form shows PUR-000002 before save.
- After save, form resets and shows PUR-000003.

---

## Checkpoint 16 — Invoice Number is Read-Only

Steps:
1. On the Purchases page, click on the invoice number field.
2. Try to type in it.

Expected:
- Field is not editable. No cursor appears. The value cannot be changed.

---

## Checkpoint 17 — Active-Only Product Picker

Steps:
1. On the Products page, deactivate "Mouse" (click Deactivate; confirm).
2. Return to the Purchases page.
3. Open the product picker dropdown.

Expected:
- "Mouse" does NOT appear in the picker.
- "Laptop" and "Sugar" are still listed.

---

## Checkpoint 18 — In-Progress Invoice Retained on Navigation

Steps:
1. On the Purchases page, add one line item (Laptop, qty 2, price 900).
2. Type "Test Supplier" in the Supplier Name field.
3. Navigate to the Products page via the sidebar.
4. Navigate back to the Purchases page.

Expected:
- The Laptop line item is still present.
- "Test Supplier" is still in the Supplier Name field.
- Running total still shows 1,800.00.
- The invoice has NOT been reset.

---

## Checkpoint 19 — Phase 2 Regression: Delete Blocked for Purchased Product

Steps:
1. On the Products page, find "Laptop" (which was just used in a purchase invoice).
2. Look at the row actions for Laptop.

Expected:
- The "Delete" button is replaced by "Deactivate" (because Laptop is now referenced
  in PurchaseItems). This confirms Phase 2's `is_product_referenced()` check works
  correctly once real purchase data exists.

---

## Checkpoint 20 — Phase 1 & 2 Regression Check

Steps:
1. Navigate to Dashboard, Sales, Reports pages via sidebar → no crash.
2. Backup Now → creates a backup file.
3. Change Password → still works.
4. Logout → returns to Login Window.
5. On Products page: search by name/SKU works; Add/Edit product still works.

Expected:
- All Phase 1 and Phase 2 features work identically to before Phase 3 was implemented.

---

## Exit Criteria

All 20 checkpoints above MUST pass before Phase 4 (Sales) work begins. Any failure
is a blocker. Key things verified:
- Multi-line purchase invoice saves atomically (header + lines + stock + price update)
- Invoice number format `PUR-XXXXXX` increments correctly
- Stock quantities increase correctly
- `purchase_price` is updated on save
- In-progress invoice survives page navigation
- Active-only picker excludes deactivated products
- Phase 2 delete-vs-deactivate guard works with real purchase data
