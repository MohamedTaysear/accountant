# Feature Specification: Purchase Invoice Management

**Feature Branch**: `003-purchases`

**Created**: 2026-06-27

**Status**: Draft

**Input**: BLUEPRINT.md Section 3.7, 6 (Purchases), 7 (Validation); IMPLEMENTATION_PLAN.md Phase 3

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Record a Purchase Invoice (Priority: P1)

The Admin builds a multi-line purchase invoice by selecting active products and entering
the quantity and unit price for each. After adding one or more lines they save the
invoice. The system records the invoice, increases each product's stock by the quantity
purchased, and updates each product's purchase price to the price entered.

**Why this priority**: This is the only mechanism by which real stock enters the system.
Without saved purchase invoices there is nothing for Phase 4 (Sales) to sell. It is
the core reason this phase exists.

**Independent Test**: Create at least one purchase invoice with two products and
different quantities. Verify the invoice number is generated as `PUR-000001`, both
products' stock quantities increase by the correct amounts, and the supplier name field
(if filled) is stored.

**Acceptance Scenarios**:

1. **Given** at least one active product exists, **When** the Admin selects a product,
   enters a quantity and unit price, clicks "Add to Invoice", and repeats for a second
   product, then clicks "Save Invoice", **Then** a new `Purchases` record is created
   with a unique `PUR-XXXXXX` invoice number, each product's `stock_quantity` is
   increased by the line's quantity, each product's `purchase_price` is updated to the
   entered price, and the page resets ready for a new invoice.

2. **Given** the Admin enters an optional supplier name, **When** the invoice is saved,
   **Then** the supplier name is stored with the invoice header and retrievable later.

3. **Given** a purchase form with no line items, **When** the Admin clicks "Save
   Invoice", **Then** the save is blocked with a clear message ("Invoice must have at
   least one item") and no database changes occur.

4. **Given** one or more line items exist, **When** the Admin clicks "Clear Invoice",
   **Then** a confirmation dialog appears; confirming resets the form to its initial
   state (no lines, blank supplier name) without touching the database.

5. **Given** no line items exist, **When** the Admin clicks "Clear Invoice", **Then**
   the form resets immediately with no confirmation dialog.

---

### User Story 2 — Active-Product Picker with Auto-Focus Flow (Priority: P1)

The Admin can quickly pick a product from a picker that shows only active products,
enter the quantity and unit price, add the line, and immediately return to the product
picker to add the next line — without touching the mouse.

**Why this priority**: Keyboard-driven data entry is a specified behavioral requirement
from the Constitution (UI Behavior Constraints). Slowing down daily invoice entry with
mouse-only interactions would significantly hurt usability for the single user.

**Independent Test**: Deactivate one product on the Products page. Open the Purchases
page and confirm that deactivated product does not appear in the picker. Add a line
using only the keyboard (pick product → Tab to Quantity → Tab to Unit Price → Enter or
click Add) and confirm focus returns to the product picker automatically.

**Acceptance Scenarios**:

1. **Given** a product has `is_active = 0`, **When** the Admin opens the Purchases
   product picker, **Then** that product does not appear in the list.

2. **Given** the Admin selects a product from the picker, **When** the selection is
   confirmed, **Then** keyboard focus moves automatically to the Quantity field.

3. **Given** the Admin fills in Quantity and Unit Price and clicks "Add to Invoice"
   (or presses Enter), **When** the line is added to the invoice table, **Then**
   keyboard focus returns automatically to the product picker, ready for the next item.

4. **Given** a quantity of 0 is entered, **When** the Admin attempts to add the line,
   **Then** the line is rejected with a clear message and the invoice table is unchanged.

5. **Given** a unit price of 0 is entered, **When** the Admin attempts to add the line,
   **Then** the line is accepted (a zero-cost purchase is valid — e.g. promotional stock).

---

### User Story 3 — Invoice Number Auto-Generation (Priority: P1)

The invoice number is auto-generated and shown read-only on the form, so the Admin
never has to type one.

**Why this priority**: Every saved purchase invoice must have a unique, human-readable
identifier. Without auto-generation the Admin could create duplicates or gaps.

**Independent Test**: Save three purchase invoices in sequence. Verify the numbers are
`PUR-000001`, `PUR-000002`, `PUR-000003`.

**Acceptance Scenarios**:

1. **Given** no purchases have been saved yet, **When** the Purchases page is opened,
   **Then** the displayed preview invoice number is `PUR-000001`.

2. **Given** N purchase invoices have been saved, **When** the Purchases page is opened,
   **Then** the displayed preview invoice number is `PUR-{N+1:06d}` (six-digit zero-padded).

3. **Given** the invoice number shown on the form, **When** the Admin tries to edit it,
   **Then** the field is read-only and cannot be changed.

---

### User Story 4 — View All Purchases History (Priority: P2)

The Admin can see a list of all past purchase invoices, filtered by date if needed.
(Full history and detailed view are part of Phase 5 Reports; this story covers the
basic history accessible to verify Phase 3 correctness.)

**Why this priority**: P2 — The history table is used in Phase 5 (Reports). Phase 3
only needs to verify that data was saved correctly, which the Products page stock update
confirms. A read-back function is needed for Phase 5 but does not need a UI in Phase 3.

**Independent Test**: After saving two purchase invoices, verify via the database
(or the Phase 5 Reports page once built) that both invoices appear with correct totals
and status = `'active'`.

**Acceptance Scenarios**:

1. **Given** purchase invoices have been saved, **When** a history query runs (used
   internally by Reports page in Phase 5), **Then** each invoice's number, supplier
   name, total amount, status, and date are retrievable.

2. **Given** a date range filter, **When** the query runs, **Then** only invoices
   within that range are returned.

---

### Edge Cases

- What happens if the Admin navigates away mid-invoice and returns? The in-progress
  invoice is retained intact (FR-026); the Admin must explicitly save or clear it.
- What happens when a product's stock quantity would become extremely large (e.g. adding 999,999 units)? Accepted — no upper stock limit is defined; the REAL column handles large values.
- What happens when the Admin saves two purchase invoices rapidly back-to-back? Each gets a unique incrementing invoice number; no duplicate can occur.
- What happens if the database is unavailable when Save Invoice is clicked? The error is caught and surfaced as a friendly message; the form is not cleared (data is not lost from the in-memory invoice).
- What happens when the Admin deactivates a product mid-invoice (in another window)? Not possible — single-user, single-window desktop app; no concurrent sessions.
- What happens when a line is added with a unit price of 0? Accepted — zero-cost purchases are valid.
- What happens when the Admin adds the same product twice to one invoice? Two separate line items are created for the same product. The stock increase and purchase_price update are applied once per line (resulting in double the total quantity increase for that product). This is intentional — a purchase may legitimately have two batches of the same item at different prices.

---

## Requirements *(mandatory)*

### Functional Requirements

**Invoice Building (in-memory, before save)**

- **FR-001**: The Purchases page MUST display an auto-generated invoice number in a
  read-only field when the page is opened or reset after a save.
- **FR-002**: The Purchases page MUST display today's date automatically in a read-only
  field (used as `created_at` for the saved record).
- **FR-003**: The Admin MUST be able to enter an optional supplier name (free text,
  no format restriction).
- **FR-004**: The product picker MUST show only active products (`is_active = 1`),
  using the single shared `get_active_products()` function.
- **FR-005**: After selecting a product from the picker, keyboard focus MUST move
  automatically to the Quantity field.
- **FR-006**: The Quantity field MUST accept decimal values greater than 0.
- **FR-007**: The Unit Price field MUST accept numeric values ≥ 0.
- **FR-008**: Clicking "Add to Invoice" MUST add a line to the invoice table showing
  Product Name, Quantity, Unit Price, and Subtotal (Quantity × Unit Price).
- **FR-009**: After a line is added, keyboard focus MUST return automatically to the
  product picker.
- **FR-010**: The invoice MUST display a running Total (sum of all line subtotals),
  recalculated automatically whenever a line is added or removed.
- **FR-011**: The Admin MUST be able to remove any line item from the invoice table
  before saving.
- **FR-012**: The Admin MUST be able to clear the entire in-progress invoice via a
  "Clear Invoice" button. If at least one line item exists, a confirmation dialog MUST
  appear first. If no line items exist, the reset happens immediately without a dialog.

**Save**

- **FR-013**: Clicking "Save Invoice" MUST be blocked (button disabled or action
  rejected) when the invoice has zero line items.
- **FR-014**: On a successful save, the system MUST write one `Purchases` header record
  and one `PurchaseItems` record per line item in a single atomic transaction.
- **FR-015**: On a successful save, the system MUST increment each purchased product's
  `stock_quantity` by the line's quantity, within the same transaction as FR-014.
- **FR-016**: On a successful save, the system MUST update each purchased product's
  `purchase_price` to the unit price entered on that line, within the same transaction.
- **FR-017**: The saved invoice MUST have a unique invoice number in the format
  `PUR-XXXXXX` (zero-padded to 6 digits, incrementing from 1).
- **FR-018**: After a successful save, the Purchases form MUST reset to its initial
  state (new invoice number generated, blank supplier name, empty line-items table).
- **FR-019**: While the save operation is in progress, the application MUST display a
  wait/busy cursor; the normal cursor MUST be restored when the operation completes
  (successfully or with an error).

**Error Handling**

- **FR-020**: If quantity is 0 or negative, the add-line action MUST be rejected with
  a clear, friendly error message; no line is added.
- **FR-021**: If unit price is negative, the add-line action MUST be rejected with a
  clear, friendly error message; no line is added.
- **FR-022**: Any database error during save MUST be caught, logged (to console), and
  shown to the Admin as a friendly message — never a raw traceback; the in-progress
  invoice data MUST be preserved on screen so the Admin can retry.
- **FR-026**: The in-progress invoice MUST be retained when the Admin navigates to
  another page and then returns to the Purchases page. The supplier name, all added
  line items, and the running total MUST remain exactly as left. The form resets only
  via an explicit "Clear Invoice" action or after a successful save.

**Data Retrieval (used by Phase 5)**

- **FR-023**: The system MUST provide a query function to retrieve all purchases,
  optionally filtered by a date range, returning invoice header fields (number, supplier,
  total, status, date).
- **FR-024**: The system MUST provide a query function to retrieve the line items for
  a specific purchase invoice.
- **FR-025**: The system MUST provide a query function to retrieve a single purchase by
  its ID (used by Invoice Detail Dialog in Phase 5).

---

### Key Entities

- **Purchase** (invoice header): Unique invoice number (`PUR-XXXXXX`), optional
  supplier name, total amount (sum of line subtotals), status (`'active'` or
  `'voided'`), creation timestamp. Never deleted — only voided.

- **PurchaseItem** (invoice line): References its parent Purchase and the purchased
  Product; stores quantity (decimal allowed), unit price at the time of purchase, and
  pre-calculated subtotal (quantity × unit price). One row per line item per invoice.

- **Product** (updated, not created): Each save increments `stock_quantity` and updates
  `purchase_price` for every product in the invoice lines.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The Admin can record a complete multi-line purchase invoice in under
  60 seconds once products exist in the catalog.
- **SC-002**: Stock quantities are updated correctly for every line item on every
  successful save — zero discrepancies between the invoice lines and the resulting
  product stock levels.
- **SC-003**: Every save attempt with zero line items is blocked before any database
  write — 100% of the time, no partial data reaches the database.
- **SC-004**: The save operation (including all stock updates) completes in under 3
  seconds for an invoice with up to 20 line items on the target Windows 10 hardware.
- **SC-005**: The invoice number sequence has zero gaps and zero duplicates across
  the entire application lifetime, including after app restarts.
- **SC-006**: Every error scenario (database failure, invalid input) surfaces a human-
  readable message — 0 raw Python tracebacks ever visible to the Admin.

---

## Assumptions

- Phase 2 (Products) is fully implemented and at least one active product exists before
  Phase 3 testing begins, per the Implementation Plan phase ordering.
- The single shared `get_active_products()` function already exists in `products_db.py`
  (built in Phase 2) and is called unchanged by the Purchases page — no duplicate
  function is created.
- Decimal quantities are allowed (e.g. 2.5 kg of bulk goods); the quantity input does
  not restrict to integers.
- There is no upper limit on the number of line items per invoice — the UI must handle
  at least 20 lines without degradation.
- Invoice numbers are generated based on the count of existing records, not via a
  separate sequence table — this is sufficient for a single-user app with no concurrent
  writes.
- `purchase_price` update (FR-016) does not track history — only the latest purchase
  price is stored. This is an explicit decision from the Blueprint's Future Extension
  Points (purchase-price history is out of scope).
- Voiding of purchase invoices is implemented in Phase 5 (Reports / Invoice Detail
  Dialog), not Phase 3. Phase 3 only needs to save and read back purchases.
- The "today's date" displayed on the form is informational only; the actual timestamp
  stored in `created_at` is set by the database at insert time (`DEFAULT
  CURRENT_TIMESTAMP`), ensuring accuracy regardless of any display lag.
- No tax/VAT calculation is included — purchase prices are entered as total line prices
  with no tax breakdown (explicitly out of scope per the Blueprint).

---

## Clarifications

### Session 2026-06-27

- Q: What happens if the same product is added twice to a purchase invoice? → A: Two
  separate line items are allowed — stock and purchase_price are updated once per line
  (net effect: quantity doubled for that product, purchase_price set to whichever line
  was processed last). This matches the Sales page behavior and is consistent with
  purchasing two batches at potentially different prices.
- Q: If the Admin partially builds an invoice and navigates to another page, then returns
  to Purchases — should the in-progress invoice be retained or reset? → A: Retained.
  The in-progress invoice (supplier name, all added lines, running total) persists
  exactly as left when the Admin returns. The Admin must explicitly click "Clear Invoice"
  or "Save Invoice" to reset the form.
