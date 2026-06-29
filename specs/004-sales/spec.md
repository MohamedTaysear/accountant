ظ# Feature Specification: Phase 4 — Sales

**Feature Branch**: `004-sales`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "read BLUEPRINT.md, IMPLEMENTATION_PLAN.md and create a specification for ## Phase 4 sales"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Build and Save a Sales Invoice (Priority: P1)

The admin user selects active products, enters quantities (including decimals), optionally enters a customer name and a discount amount, reviews the automatically calculated grand total, and saves the invoice. Saving atomically records the invoice header, all line items, and decrements stock for each product sold — all in a single operation.

**Why this priority**: This is the core revenue-recording action. Without the ability to create and save a sales invoice, no other part of Phase 4 (stock reduction, discount calculation, invoice numbering) is testable or meaningful.

**Independent Test**: Can be fully tested by creating a purchase invoice first (via the existing Phase 3 screen) to stock products, then building a sales invoice against those products and verifying the stock levels drop correctly on the Products page.

**Acceptance Scenarios**:

1. **Given** the Sales page is open and at least one product has sufficient stock, **When** the user selects a product, enters a valid quantity (including a decimal like 2.5), clicks "Add to Invoice", and then clicks "Save Invoice", **Then** the invoice is saved with a unique number in the format `SAL-000001`, the product's stock quantity is decremented by the sold amount, and a success message is shown with the invoice number.
2. **Given** a saved invoice and the user navigates to the Products page, **When** they look at the sold product's stock, **Then** the stock quantity reflects the reduction from the sale.
3. **Given** the user enters a discount amount, **When** the discount is applied, **Then** the Grand Total shown equals (sum of line subtotals) − Discount, and this Grand Total is what is stored in the database.
4. **Given** the user attempts to save an invoice with zero line items, **When** they click "Save Invoice", **Then** the action is blocked with a clear message and no database record is created.
5. **Given** the user has entered line items, **When** they click "Clear Invoice", **Then** a confirmation dialog appears; confirming resets the form to empty; cancelling leaves the lines intact.

---

### User Story 2 — Stock Availability Validation (Priority: P2)

Before a line can be added to the in-progress invoice, the system verifies that the requested quantity does not exceed the product's current stock. If it does, the line is rejected with a clear message before any data is written.

**Why this priority**: Prevents overselling. Without this guard, the store could record more units sold than physically available, corrupting stock accuracy for all downstream reporting and purchasing decisions.

**Independent Test**: Can be fully tested independently by stocking a product to a known quantity via a purchase invoice, then attempting to add a line to a sales invoice that exceeds that quantity — the block must trigger. A second attempt with a valid quantity must succeed.

**Acceptance Scenarios**:

1. **Given** a product has 10 units in stock, **When** the user attempts to add a line for 15 units of that product, **Then** the line is rejected with a clear error message and the in-progress invoice remains unchanged.
2. **Given** a product has 10 units in stock, **When** the user adds a line for exactly 10 units, **Then** the line is accepted and added to the invoice.
3. **Given** a product has 0 units in stock, **When** the user attempts to add that product to the invoice, **Then** the line is rejected before reaching the database.

---

### User Story 3 — Discount Validation (Priority: P3)

The admin can apply an invoice-level discount amount. The system ensures the discount never causes the grand total to go negative — a discount greater than the invoice subtotal is rejected before saving.

**Why this priority**: Protects financial data integrity. A negative total amount would be meaningless and would distort all reporting totals.

**Independent Test**: Can be fully tested independently of US1 and US2 by building an invoice and attempting to apply a discount larger than the subtotal.

**Acceptance Scenarios**:

1. **Given** the invoice subtotal is 100, **When** the user enters a discount of 150, **Then** the Grand Total label immediately shows 0 (not −50), the discount field is highlighted in red (or shows an inline error), and clicking "Save Invoice" is blocked with a clear message until the discount is corrected.
2. **Given** the invoice subtotal is 100, **When** the user enters a discount of exactly 100, **Then** the Grand Total shows 0 and the invoice saves successfully (a fully discounted invoice is valid).
3. **Given** the user changes the discount field, **When** any value is entered, **Then** the Grand Total label updates in real time without requiring an explicit "recalculate" step.
4. **Given** the discount field is showing a red error state (discount > subtotal), **When** the user corrects the discount to a valid value, **Then** the red highlight clears immediately and the Save Invoice action becomes available.

---

### User Story 4 — In-Progress Invoice Retained on Navigation (Priority: P4)

Navigating away from the Sales page (e.g. to check current stock on the Products page) and then returning does not wipe out the in-progress invoice — all line items and entered values are preserved until the user explicitly saves or clears them.

**Why this priority**: Without retention, the user loses work every time they need to look something up mid-invoice. This behavior mirrors what is already implemented for the Purchases page (FR-026 equivalent).

**Independent Test**: Can be fully tested by adding lines to a sales invoice, clicking away to Products, clicking back to Sales, and verifying all lines are still present.

**Acceptance Scenarios**:

1. **Given** the user has added two line items to a sales invoice, **When** they navigate to the Products page and then back to Sales, **Then** both line items are still present in the invoice table and no data is lost.
2. **Given** the user has partially filled in a supplier/customer name field, **When** they navigate away and return, **Then** the customer name field still contains what was typed.

---

### Edge Cases

- What happens when the only active product has 0 stock? The product still appears in the picker but adding a line for any quantity > 0 is blocked at validation.
- What if two line items for the same product are added? Each is treated as a separate line; stock is decremented twice in the same transaction. At line-add time, the availability check MUST account for quantities already queued for that product in the current in-progress invoice — the effective available quantity is `DB stock_quantity − sum of already-queued quantities for that product_id`. This prevents two individually valid lines from combining to exceed available stock.
- What if the database write fails mid-transaction (e.g. disk error)? The entire transaction is rolled back; no partial invoice or stock change is persisted.
- What if the user applies a discount of 0? This is valid; the invoice saves normally with no discount effect.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST generate a unique invoice number in the format `SAL-NNNNNN` (e.g. `SAL-000001`) for each saved sales invoice, derived from the database primary key.
- **FR-002**: The Sales page MUST display the next expected invoice number as a read-only label before the invoice is saved.
- **FR-003**: The Sales page MUST display the current date as a read-only label.
- **FR-004**: The user MUST be able to enter an optional customer name (free-text, no format restriction).
- **FR-005**: The product picker MUST show only active products; deactivated products MUST NOT appear.
- **FR-006**: After selecting a product, focus MUST automatically move to the Quantity input.
- **FR-007**: The quantity input MUST accept decimal values (e.g. 2.5).
- **FR-008**: When a line is added, the system MUST validate that the entered quantity does not exceed the product's *effective available stock*, defined as `DB stock_quantity − sum of quantities already queued for that product in the current in-progress invoice`; if validation fails, the line MUST be rejected with a clear message and the invoice must remain unchanged.
- **FR-009**: Each line's subtotal MUST be calculated as quantity × the product's current selling price at the time the line is added.
- **FR-010**: The invoice Subtotal (sum of all line subtotals) MUST be displayed and update automatically as lines are added or removed.
- **FR-011**: The user MUST be able to enter a discount amount at the invoice level (numeric, ≥ 0).
- **FR-012**: The system MUST reject saving when the discount exceeds the invoice Subtotal (Grand Total can never be stored as a negative value).
- **FR-013**: The Grand Total MUST display as Subtotal − Discount and MUST update in real time whenever the discount changes. If the discount exceeds the Subtotal, the Grand Total display MUST be clamped to 0 (never shown as negative) and the discount input field MUST immediately show a visual error state (e.g. highlighted in red or accompanied by an inline validation message) to signal the invalid value; the Save Invoice action remains blocked until the discount is corrected.
- **FR-013a**: The visual error state on the discount field MUST clear as soon as the discount value falls back to ≤ Subtotal.
- **FR-014**: The user MUST be able to remove individual line items from the in-progress invoice before saving.
- **FR-015**: The "Clear Invoice" button MUST require confirmation if one or more line items exist; if the invoice is already empty, it MUST clear without a prompt.
- **FR-016**: The "Save Invoice" action MUST be blocked if the invoice has no line items.
- **FR-017**: On save, the system MUST atomically: insert one `Sales` row (storing `total_amount` = Grand Total, `discount_amount`, `customer_name`), insert one `SaleItems` row per line (storing `quantity`, `unit_price`, `purchase_price_at_sale`, `subtotal`), and decrement each sold product's `stock_quantity` — all in a single transaction; any failure MUST rollback the entire transaction.
- **FR-018**: The `purchase_price_at_sale` field MUST be captured from the product's current purchase price at the moment of saving, not at line-add time.
- **FR-019**: After a successful save, the form MUST reset to an empty invoice with a new preview invoice number, and a success message MUST be shown containing the saved invoice number.
- **FR-020**: The Sales page MUST retain all in-progress line items and entered values when the user navigates away and returns within the same session.
- **FR-021**: A busy/wait cursor MUST be displayed for the duration of the Save Invoice action.
- **FR-022**: After returning to the Sales page from another page, the product list MUST be refreshed (to pick up any stock or active-status changes made on the Products or Purchases pages).

### Key Entities

- **Sales** (invoice header): invoice_number, customer_name, discount_amount, total_amount (= grand total after discount), status ('active' or 'voided'), created_at.
- **SaleItems** (invoice line): sale_id, product_id, quantity, unit_price (selling price at time of sale), purchase_price_at_sale (purchase price at time of save — for profit calculation), subtotal (quantity × unit_price).
- **Products** (updated on save): stock_quantity decremented by quantity sold per line.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A complete multi-line sales invoice (2+ products, with a discount) can be created and saved in under 2 minutes from a standing start.
- **SC-002**: Every successful save correctly decrements stock for all sold products — verified by comparing Products page stock values before and after the sale with 100% accuracy.
- **SC-003**: Attempting to sell more units than available stock is blocked 100% of the time before any database write occurs.
- **SC-004**: Attempting to apply a discount greater than the subtotal is blocked 100% of the time before any database write occurs.
- **SC-005**: After navigating away from a partially built invoice and returning, 100% of entered data (lines, customer name, discount) is preserved.
- **SC-006**: Saving an invoice is an atomic operation — in no scenario does a partial invoice or partial stock change persist after a failure.
- **SC-007**: Invoice numbers follow the `SAL-NNNNNN` format and are globally unique across all saved invoices.

---

## Assumptions

- Phase 3 (Purchases) is complete and has been manually verified: active products with non-zero stock already exist in the database before Phase 4 testing begins.
- The `Sales` and `SaleItems` tables are already created by `database.py` (the schema was defined in Phase 1 and has not changed).
- The existing `products_db.get_active_products()` function is the sole source for the product picker — no new DB function is needed to list products for sale (same function already used by the Purchases page).
- The `purchase_price_at_sale` value is read at save-time from `Products.purchase_price`, which is always the most recent purchase price. Historical accuracy for earlier purchases is not a concern for Phase 4 (that accuracy is provided by previously saved `PurchaseItems` records).
- Invoice numbering uses `MAX(id) + 1` from the `Sales` table as the preview and `lastrowid` after insert for the final number — the same pattern already used by the Purchases page.
- The discount field defaults to 0 (no discount) and the user may leave it at 0 without any error.
- Customer Name is entirely optional — no validation beyond it being a plain text field. An empty customer name is stored as NULL.
- The in-progress invoice lives only in UI memory (a Python list); it is not persisted to disk or the database until the user explicitly saves.
- Focus auto-returns to the product picker after each successful line-add, so the user can immediately select the next product without a mouse click.
- Layered architecture constraints from the Constitution apply: `ui/sales_page.py` MUST NOT import `sqlite3` directly; all business logic lives in `logic/sales_logic.py`; all SQL lives in `sales_db.py`.

---

## Clarifications

### Session 2026-06-27

- Q: Should `purchase_price_at_sale` be captured at line-add time or at invoice-save time? → A: At invoice-save time — it reads the product's current `purchase_price` at the moment of the DB write. This matches the Blueprint specification ("captured from the product's current purchase price at save-time").
- Q: When the same product appears in more than one line of the in-progress invoice, how should stock availability be validated at line-add time? → A: Option B — validate against DB stock minus quantities already queued for that product in the current invoice (effective available stock). Prevents combined overselling within one invoice.
- Q: When the discount exceeds the subtotal mid-edit, what should the Grand Total label display and should there be immediate feedback? → A: Option A — clamp Grand Total display to 0 (never go negative); immediately highlight the discount field in red (or show inline validation message) while the discount is invalid; Save remains blocked until corrected; visual error clears as soon as the discount is valid again.
