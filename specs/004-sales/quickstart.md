# Quickstart Validation Guide: Phase 4 — Sales

**Date**: 2026-06-27
**Purpose**: Manual end-to-end validation scenarios that prove Phase 4 is complete and correct. Run these after implementation, before considering the phase done.

---

## Prerequisites

1. Phase 3 (Purchases) manually verified and passing all checkpoints.
2. At least two active products with non-zero stock exist (created via the Purchases page).
3. The application launches successfully and you are logged in.
4. The `data/store.db` database is in a known-good state (or freshly reset if testing from scratch).

**Suggested setup** (if starting fresh — delete `data/store.db` first):
- Log in as admin.
- Products page: Add "Widget A" (category: Electronics, purchase price: 10, selling price: 25, stock: 0, reorder: 5).
- Products page: Add "Widget B" (category: Electronics, purchase price: 5, selling price: 15, stock: 0, reorder: 3).
- Purchases page: Create a purchase invoice — Widget A × 20, Widget B × 10 → Save.
- Confirm stock: Widget A = 20, Widget B = 10 on the Products page.

---

## Checkpoint 1 — Basic Invoice Creation and Save

**Goal**: Verify a multi-line invoice saves correctly and decrements stock.

Steps:
1. Navigate to the Sales page.
2. Confirm the invoice number label shows `SAL-000001` (or the next expected number).
3. Confirm today's date is displayed (read-only).
4. Select "Widget A" from the product picker.
5. Confirm focus automatically moves to the Quantity input.
6. Enter quantity `3` → click "Add to Invoice".
7. Confirm focus returns to the product picker.
8. Select "Widget B", enter quantity `2` → click "Add to Invoice".
9. Confirm the line-items table shows both lines with correct subtotals (Widget A: 75, Widget B: 30).
10. Confirm the Subtotal label shows 105.
11. Leave Discount at 0. Confirm Grand Total shows 105.
12. Enter customer name "Test Customer".
13. Click "Save Invoice".
14. Confirm a success message appears containing "SAL-000001".
15. Confirm the form resets to empty with a new invoice number preview (`SAL-000002`).
16. Navigate to Products page. Confirm Widget A stock = 17, Widget B stock = 8.

**Expected result**: ✓ Invoice saved, stock decremented correctly.

---

## Checkpoint 2 — Stock Availability Validation (single product)

**Goal**: Verify the system blocks a line that exceeds available stock.

Steps:
1. Navigate to the Sales page (invoice should be empty).
2. Select "Widget A" (current stock: 17 from Checkpoint 1).
3. Enter quantity `20` → click "Add to Invoice".
4. Confirm a clear error message appears (stock exceeded) and no line is added to the table.
5. Enter quantity `17` → click "Add to Invoice".
6. Confirm the line is accepted (exactly 17 ≤ 17).

**Expected result**: ✓ Oversell blocked; exact-stock quantity accepted.

---

## Checkpoint 3 — Effective Stock Validation (same product, two lines)

**Goal**: Verify that adding a second line for the same product accounts for already-queued quantity.

Steps:
1. Start with a fresh invoice (click Clear if needed, or start from end of Checkpoint 2).
2. If continuing from Checkpoint 2, the invoice already has Widget A × 17.
3. Attempt to add Widget A × 1 (stock is 17 in DB, but 17 already queued → effective available = 0).
4. Confirm the line is rejected with a clear error.
5. Click "Clear Invoice" → confirm and clear.
6. Add Widget A × 10 → accepted.
7. Add Widget A × 5 → effective available = 17 − 10 = 7; 5 ≤ 7 → accepted.
8. Attempt Widget A × 5 again → effective available = 17 − 15 = 2; 5 > 2 → rejected.

**Expected result**: ✓ Effective available stock correctly accounts for already-queued lines.

---

## Checkpoint 4 — Discount Validation and Grand Total Display

**Goal**: Verify discount logic, real-time Grand Total update, and inline error feedback.

Steps:
1. Start with a fresh invoice.
2. Add Widget A × 2 (subtotal = 50), Widget B × 2 (subtotal = 30). Subtotal = 80.
3. Enter discount `30` → confirm Grand Total shows 50 (80 − 30). No error state.
4. Change discount to `100` → confirm Grand Total immediately shows 0 (clamped, not −20), and the discount field shows a red highlight or inline error.
5. Attempt "Save Invoice" → confirm save is blocked with a message about the discount.
6. Change discount back to `20` → confirm red highlight disappears and Grand Total shows 60.
7. Click "Save Invoice" → invoice saves successfully with total_amount = 60.

**Expected result**: ✓ Grand Total clamped at 0 when discount > subtotal; visual error shown; save blocked; clears when corrected.

---

## Checkpoint 5 — Zero Line Items Blocked

**Goal**: Verify that saving an empty invoice is blocked.

Steps:
1. Open the Sales page with an empty invoice.
2. Click "Save Invoice" without adding any lines.
3. Confirm a clear error message appears and no DB record is created.

**Expected result**: ✓ Empty invoice save blocked.

---

## Checkpoint 6 — Clear Invoice Confirmation

**Goal**: Verify the confirmation dialog behaviour for Clear Invoice.

Steps:
1. Add one or more lines to the in-progress invoice.
2. Click "Clear Invoice" → confirm a dialog appears asking to confirm.
3. Choose "Cancel" → invoice lines remain intact.
4. Click "Clear Invoice" again → choose "Yes" → invoice is cleared.
5. Click "Clear Invoice" with no lines → confirm it clears instantly without a dialog.

**Expected result**: ✓ Confirmation required when lines exist; no confirmation when empty.

---

## Checkpoint 7 — In-Progress Invoice Retained on Navigation

**Goal**: Verify navigation away and back does not lose work.

Steps:
1. Add two lines to the in-progress invoice. Enter a customer name and a discount.
2. Click "Products" in the sidebar → navigate away.
3. Click "Sales" in the sidebar → return to Sales page.
4. Confirm all line items, customer name, and discount value are still present exactly as entered.
5. Confirm the product picker has refreshed (any changes made on Products page are reflected).

**Expected result**: ✓ In-progress invoice fully retained; product list refreshed.

---

## Checkpoint 8 — Only Active Products in Picker

**Goal**: Verify deactivated products do not appear in the Sales picker.

Steps:
1. On the Products page, deactivate "Widget B".
2. Navigate to the Sales page.
3. Confirm "Widget B" does NOT appear in the product picker.
4. Reactivate "Widget B" on the Products page.
5. Navigate back to Sales and confirm "Widget B" reappears.

**Expected result**: ✓ Active-only picker rule enforced consistently.

---

## Checkpoint 9 — Wait Cursor on Save

**Goal**: Verify the busy cursor is shown during Save Invoice.

Steps:
1. Add a line and click "Save Invoice".
2. Observe that the cursor changes to a wait/busy cursor for the duration of the save (brief but visible).
3. Confirm normal cursor is restored after the success message.

**Expected result**: ✓ Wait cursor shown during save operation.

---

## Checkpoint 10 — Invoice Number Sequence

**Goal**: Verify invoice numbers increment correctly across saves.

Steps:
1. Save a sales invoice → note invoice number (e.g. `SAL-000002`).
2. Save another → confirm the number increments by 1 (`SAL-000003`).
3. Check: the preview number shown before saving matches the actual saved number.

**Expected result**: ✓ Sequential, gap-free invoice numbers; preview matches actual.

---

## Checkpoint 11 — No Regressions (Phases 1–3)

**Goal**: Confirm Phases 1, 2, and 3 features still work after Phase 4 changes.

Steps:
1. Log out → log back in (credentials unchanged).
2. Products page: add, edit, search — all functional.
3. Purchases page: create a new purchase invoice — saves correctly, stock increases.
4. Confirm the Purchases page product picker still shows active products only.
5. Navigate all sidebar pages — no crashes.

**Expected result**: ✓ All prior functionality intact.

---

## Pass Criteria

All 11 checkpoints must pass without error before Phase 4 is considered complete.
Phase 5 (Dashboard & Reports) may not begin until these checkpoints are verified.
