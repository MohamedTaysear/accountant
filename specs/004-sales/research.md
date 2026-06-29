# Research: Phase 4 — Sales

**Date**: 2026-06-27
**Status**: Complete — no NEEDS CLARIFICATION items remain

## Overview

Phase 4 introduces no new technology, no new architectural patterns, and no external integrations. All decisions are fully established by Phases 1–3. This document records the key decisions that carry forward into this phase to give the implementer a single reference point.

---

## Decision 1: Invoice Save Transaction Pattern

**Decision**: Save Sales invoice using the same single-transaction pattern as Purchases: open connection → INSERT Sales header → capture `lastrowid` → derive invoice number → UPDATE header with invoice number → INSERT one SaleItems row per line → UPDATE each product's `stock_quantity` → commit; rollback entire transaction on any error.

**Rationale**: Constitution Principle IV mandates single-transaction atomic saves for all multi-table operations. The Purchases page (`purchases_db.py`) already implements this pattern successfully. Reusing it guarantees consistency and eliminates the risk of partial saves leaving orphaned invoice headers or incorrect stock values.

**Alternatives considered**: Committing the header first then inserting lines — rejected because any failure mid-insert would leave a header row with no items and no stock change, corrupting the audit trail.

---

## Decision 2: Invoice Numbering

**Decision**: `SAL-{id:06d}` where `id` is the database-assigned primary key from the `Sales` table. Preview number uses `MAX(id) + 1`; final number uses `lastrowid` after insert.

**Rationale**: Identical to the Purchases numbering scheme (`PUR-{id:06d}`). Using `lastrowid` is safe for a single-user local app — no concurrent writes possible. The preview is advisory only; the actual number is always derived from the DB.

**Alternatives considered**: UUID-based numbers — rejected; the Blueprint specifies sequential formatted numbers. Sequence table — rejected; unnecessary complexity for a single-user app.

---

## Decision 3: Effective Available Stock Validation

**Decision**: When the user adds a line, the available stock check uses **effective available stock = DB `stock_quantity` − sum of quantities already queued for that `product_id` in the current in-progress invoice**. This is computed in the logic layer from the in-memory `_items` list, with no additional DB query needed.

**Rationale**: Prevents two individually valid lines from combining to exceed available stock within a single invoice (clarified during `/speckit-clarify` — spec FR-008). The in-memory list is the authoritative source of queued quantities since the invoice has not yet been saved.

**Alternatives considered**: Validate only against DB stock — rejected because this allows overselling within a single invoice (e.g. product with 10 units: add 8 units line 1, add 5 units line 2 — both pass DB check but combined total is 13).

---

## Decision 4: Discount Display and Validation UX

**Decision**: Grand Total display is clamped to 0 when discount > subtotal (never shown as negative). Discount field shows a visual error state (red stylesheet) in real time when discount > subtotal. Save is blocked until the discount is corrected. Error state clears immediately when discount ≤ subtotal.

**Rationale**: Clarified during `/speckit-clarify` — spec FR-013, FR-013a. Clamping prevents confusing negative-total display. Inline feedback is immediate (no need to click Save to discover the error).

**Alternatives considered**: Show actual negative value — rejected because it implies the store owes money to the customer, which is not a supported concept.

---

## Decision 5: `purchase_price_at_sale` Capture Timing

**Decision**: Read from `Products.purchase_price` at the moment of the DB write (save-time), not at line-add time.

**Rationale**: Matches Blueprint specification §6 Sales: "purchase_price_at_sale is captured from the product's current purchase price at save-time." Captured in the save transaction alongside the `SaleItems` insert, ensuring the freeze happens atomically with the rest of the save.

**Alternatives considered**: Capture at line-add time — rejected per Blueprint; would require storing it in the in-memory `_items` dict and would reflect the price at an earlier moment, potentially missing a price update that happened between line-add and save.

---

## Decision 6: Active Products Picker

**Decision**: Reuse `products_db.get_active_products()` — the identical function already used by the Purchases page picker. No new DB function needed.

**Rationale**: Constitution Principle IV states "There MUST be exactly one shared function for fetching active products, reused by both screens." Using a separate function would violate this principle and risk divergence.

**Alternatives considered**: New `get_products_for_sale()` function — rejected; would duplicate `get_active_products()` and violate the single-function rule.

---

## Decision 7: In-Progress Invoice Navigation Retention

**Decision**: `showEvent` calls only `_reload_products()` (to refresh the active-product list), NOT `_reset_form()`. The in-progress `_items` list and all entered field values persist in UI memory across navigation events.

**Rationale**: Matches the Purchases page pattern (FR-026 equivalent). Resetting on `showEvent` would destroy work-in-progress every time the user navigates away to check stock or add a product. The reload ensures the product picker reflects any changes made on the Products or Purchases pages.

**Alternatives considered**: Reset on `showEvent` — rejected per spec US4 and FR-020; destroys in-progress work.
