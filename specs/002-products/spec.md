# Feature Specification: Product Catalog Management

**Feature Branch**: `002-products`

**Created**: 2026-06-27

**Status**: Draft

**Input**: Phase 2 of the Store Accounting System Implementation Plan — replace the
Products placeholder page with full product catalog management, including add, edit,
delete/deactivate, search, and active/inactive state control.

---

## User Scenarios & Testing

### User Story 1 — Add a New Product (Priority: P1)

The Admin adds a new product to the catalog by filling in the product's details in a
popup dialog. The new product immediately appears in the product list.

**Why this priority**: Adding products is the prerequisite for every other feature in
the system — no purchase, sale, or stock level can exist without at least one product.
This is the MVP of the Products phase.

**Independent Test**: Open the Products page, click Add Product, fill in all fields,
save — the new product appears in the table. Repeat with a minimal input (name only,
all defaults) and with a full input including SKU, unit, prices, stock, and reorder
level.

**Acceptance Scenarios**:

1. **Given** the Products page is open, **When** the user clicks "Add Product",
   **Then** a modal dialog opens with empty/defaulted fields.
2. **Given** the Add Product dialog is open with valid data, **When** the user clicks
   Save, **Then** the dialog closes and the new product appears in the product table
   immediately.
3. **Given** the Add Product dialog is open, **When** the user enters a Name and
   leaves all other fields at their defaults (Unit = "pcs", prices = 0, stock = 0,
   reorder level = 5), **Then** the product saves successfully with those defaults.
4. **Given** the Add Product dialog is open, **When** the user enters a stock quantity
   of 2.5 (decimal), **Then** it saves and displays correctly.
5. **Given** the Add Product dialog is open with an empty Name field, **When** the
   user clicks Save, **Then** an error is shown and the dialog stays open.
6. **Given** the Add Product dialog is open with a negative Selling Price, **When**
   the user clicks Save, **Then** an error is shown and the dialog stays open.

---

### User Story 2 — Edit an Existing Product (Priority: P1)

The Admin updates a product's details by clicking Edit on its row, making changes in
the same dialog used for adding, and saving.

**Why this priority**: Product details change over time (prices, reorder levels, unit
types). Without edit, the catalog becomes stale. Depends on US1 (product must exist
first).

**Independent Test**: Add a product (US1), then click Edit on its row, change the
selling price and reorder level, save — changes persist after the dialog closes and
survive an app restart.

**Acceptance Scenarios**:

1. **Given** a product exists in the table, **When** the user clicks Edit on its row,
   **Then** the same dialog opens with all fields pre-filled with that product's
   current values.
2. **Given** the Edit dialog is open with modified values, **When** Save is clicked,
   **Then** the dialog closes and the updated values appear in the table immediately.
3. **Given** the Edit dialog is open, **When** the user clicks Cancel, **Then** the
   dialog closes and the product's values are unchanged.
4. **Given** a product is edited to change its Name, **When** the app is restarted and
   the Products page is opened, **Then** the new name persists correctly.

---

### User Story 3 — Delete or Deactivate a Product (Priority: P1)

Products that have never been used in any invoice can be permanently deleted. Products
that have invoice history cannot be deleted — their Delete button is replaced by a
Deactivate button, which hides them from daily use without destroying history.
Deactivated products can be reactivated.

**Why this priority**: Without the ability to remove or archive products, the catalog
fills with clutter. The delete/deactivate distinction is a core data-integrity rule
that protects invoice history.

**Independent Test**: Add a product that has never been invoiced — Delete is available
and works. (The "used product" path — deactivate/reactivate — is verified once
Purchases are introduced in Phase 3.)

**Acceptance Scenarios**:

1. **Given** a product has never appeared in any invoice, **When** the user clicks
   Delete on its row, **Then** a confirmation dialog appears.
2. **Given** the confirmation dialog is shown, **When** the user confirms deletion,
   **Then** the product is permanently removed from the table.
3. **Given** the confirmation dialog is shown, **When** the user cancels, **Then**
   the product remains in the table unchanged.
4. **Given** a product HAS appeared in at least one invoice, **When** the user views
   its row, **Then** a Deactivate button is shown instead of Delete.
5. **Given** a product HAS appeared in at least one invoice, **When** the user clicks
   Deactivate and confirms, **Then** the product disappears from the default table
   view (it is now inactive).
6. **Given** an inactive product exists, **When** the user checks "Show Inactive",
   **Then** the inactive product appears in the table with a status indicator.
7. **Given** an inactive product is visible (Show Inactive checked), **When** the user
   clicks Activate on its row, **Then** the product becomes active again and appears
   in the normal table view.

---

### User Story 4 — Search the Product Catalog (Priority: P2)

The Admin can filter the product list in real time by typing in a search box, which
matches against both product name and SKU.

**Why this priority**: Once the catalog has more than a handful of products, scrolling
becomes impractical. Search makes the catalog usable at scale. Depends on US1.

**Independent Test**: Add several products with distinct names and SKUs. Type a partial
name → only matching products show. Clear search → all products show. Type a partial
SKU → only matching products show.

**Acceptance Scenarios**:

1. **Given** products exist with varying names, **When** the user types a partial name
   in the search box, **Then** only products whose name contains the typed text
   (case-insensitive) are shown.
2. **Given** products exist with SKUs, **When** the user types a partial SKU in the
   search box, **Then** only products whose SKU contains the typed text
   (case-insensitive) are shown.
3. **Given** the search box contains text, **When** the user clears the search box,
   **Then** all products (matching the active/inactive filter) are shown again.
4. **Given** inactive products exist, **When** the user searches with "Show Inactive"
   unchecked, **Then** inactive products are excluded from search results.
5. **Given** inactive products exist, **When** the user searches with "Show Inactive"
   checked, **Then** inactive products are included in search results.

---

### Edge Cases

- What happens when a product SKU is left blank? Multiple products may have a blank
  SKU — only duplicate non-null SKUs are rejected.
- What happens when a duplicate non-null SKU is entered? The save is rejected with a
  specific "SKU already in use" message (not a raw database error).
- What happens when the selling price is lower than the purchase price? The save
  proceeds but a warning is shown to the user (not a blocking error).
- What happens when stock quantity or reorder level contains a decimal value?
  Decimals (e.g. 2.5 kg) are accepted and stored correctly.
- What happens when the user deletes the only product in the catalog? The table
  becomes empty — no crash.
- What happens when a search yields zero results? The table shows empty — a message
  indicating no results is displayed.

---

## Requirements

### Functional Requirements

- **FR-001**: The system MUST display all active products in a table with columns:
  Name, SKU, Unit, Purchase Price, Selling Price, Stock Quantity, Reorder Level,
  Status.
- **FR-002**: The system MUST provide a search box that filters the product list by
  partial name OR partial SKU match, case-insensitively, as the user types or on Enter.
- **FR-003**: The system MUST provide a "Show Inactive" checkbox (unchecked by default)
  that, when checked, includes deactivated products in both the table and search
  results.
- **FR-004**: The system MUST provide an "Add Product" button that opens a modal dialog
  for entering new product details.
- **FR-005**: The Add/Edit dialog MUST include fields: Name (required), SKU (optional),
  Unit (defaults to "pcs"), Purchase Price (required, ≥ 0), Selling Price (required,
  ≥ 0), Stock Quantity (required, ≥ 0, decimals allowed), Reorder Level (required,
  ≥ 0, decimals allowed).
- **FR-006**: The system MUST validate all required fields before saving; invalid input
  MUST be rejected with a clear, field-specific error message and the dialog MUST
  remain open.
- **FR-007**: If a non-null SKU is entered that already exists for another product, the
  save MUST be rejected with a specific "SKU already in use" message.
- **FR-008**: If the Selling Price entered is less than the Purchase Price, the system
  MUST display a non-blocking warning but MUST still allow the save to proceed.
- **FR-009**: Clicking Edit on a product row MUST open the same dialog pre-filled with
  that product's current values; saving MUST update the product in place.
- **FR-010**: For a product that has NEVER appeared in any invoice, the system MUST
  show a Delete action; clicking Delete MUST require confirmation before permanent
  removal.
- **FR-011**: For a product that HAS appeared in at least one invoice, the system MUST
  show a Deactivate action instead of Delete; clicking Deactivate MUST require
  confirmation before hiding the product.
- **FR-012**: Deactivating a product MUST hide it from the default product table view,
  from the Sales product picker, and from the Purchases product picker — consistently
  across all screens.
- **FR-013**: An inactive product MUST be reactivatable via an Activate action visible
  when "Show Inactive" is checked.
- **FR-014**: All product changes (add, edit, delete, deactivate, reactivate) MUST
  persist to storage immediately and survive an application restart.
- **FR-015**: Every storage error, validation failure, and constraint violation MUST be
  shown to the user as a friendly message; a raw error trace MUST never reach the user.

### Key Entities

- **Product**: Represents a single catalog item. Attributes: Name (required text),
  SKU (optional unique code), Unit (text, e.g. "pcs", "kg"), Purchase Price (decimal ≥ 0),
  Selling Price (decimal ≥ 0), Stock Quantity (decimal ≥ 0, supports fractional units),
  Reorder Level (decimal ≥ 0, triggers Low Stock alert when stock falls to or below
  this), Active/Inactive status (controls visibility across all screens).

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: A new product with all fields filled can be added and appears in the
  table in under 2 seconds.
- **SC-002**: Editing a product's price and saving completes in under 2 seconds, with
  the updated price visible in the table immediately.
- **SC-003**: A product that has never been invoiced can be permanently deleted; the
  table updates immediately with no crash.
- **SC-004**: Typing a partial product name or SKU in the search box filters the table
  within 1 second.
- **SC-005**: All validation rules (empty name, negative price, duplicate SKU, negative
  stock, negative reorder level) are enforced — 100% of invalid inputs rejected with
  a clear message before any storage operation.
- **SC-006**: The active/inactive state is consistent: a deactivated product is absent
  from the product table (when "Show Inactive" is unchecked), the Sales product picker,
  and the Purchases product picker — verified across all three locations simultaneously.
- **SC-007**: All manual testing checkpoints defined in the Implementation Plan for
  Phase 2 pass in a single continuous test session with no regressions from Phase 1.

---

## Assumptions

- The Products page replaces the Phase 1 placeholder; the placeholder file is
  completely overwritten — no placeholder code is retained.
- The Product Dialog (Add/Edit popup) is a separate file reused for both Add and Edit
  operations; the distinction is controlled by whether an existing product ID is passed
  in.
- The "Show Inactive" checkbox state is not persisted between sessions — it always
  resets to unchecked when the page is opened or the app is restarted.
- Search filtering happens on every keystroke (live filter) as well as on Enter — no
  separate "Search" button is required.
- The Name field maximum length is 100 characters; no explicit maximum is enforced on
  SKU or Unit fields beyond what the storage layer's text type allows.
- The selling-price-below-purchase-price warning is a `QMessageBox` shown before the
  save completes, giving the user one more chance to correct it — but if they confirm,
  the save proceeds.
- Phase 2 does not implement the Low Stock list on the Dashboard; that is Phase 5.
  However, the `reorder_level` field must be stored correctly in Phase 2 so Phase 5
  can use it without a schema change.
- The "used in an invoice" check (which determines Delete vs Deactivate) looks at
  both `SaleItems` and `PurchaseItems` tables. At the end of Phase 2, no invoices
  exist yet, so all products can be deleted — the Deactivate path is first exercised
  in Phase 3 when purchase invoices are created.
