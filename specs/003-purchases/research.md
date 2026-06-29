# Research: Purchase Invoice Management

**Feature**: 003-purchases
**Date**: 2026-06-27
**Status**: Complete — all decisions pre-made in `BLUEPRINT.md` and `IMPLEMENTATION_PLAN.md`

No open unknowns existed at planning time. This document records the rationale for
each key technical decision.

---

## Decision Log

### Logic Layer Required (unlike Phase 2 Products)

**Decision**: Phase 3 introduces `logic/purchase_logic.py` as a mandatory middle layer
between `ui/purchases_page.py` and `purchases_db.py`.

**Rationale**: Unlike Phase 2 (pure CRUD with no cross-table transactions), Purchases
requires:
- In-memory invoice building (accumulating line items before any DB write)
- Multi-table atomic transaction (Purchases header + PurchaseItems rows + stock
  increments + purchase_price updates — all in one commit)
- Quantity validation (> 0 per line)
- Running total calculation (sum of line subtotals)

These are business rules that MUST live in the logic layer per Constitution Principle I.
The UI page manages display and user interaction only; the DB file executes parameterized
SQL only.

**Alternatives considered**: Putting the transaction inside `purchases_db.py` only —
rejected because line-item validation and total calculation are business logic, not SQL.
Putting the transaction in the UI — rejected as a Constitution violation.

---

### Invoice Numbering Strategy

**Decision**: Generate invoice numbers as `PUR-XXXXXX` (six-digit zero-padded) using
`MAX(id)` or `COUNT(*)` on the `Purchases` table to determine the next sequence number
at save-time, not displayed-time.

**Rationale**: The display preview on the form shows the *expected* next number
(`MAX(id) + 1`). The actual unique number is confirmed and stored only at save-time.
For a single-user app with no concurrent writes, this is safe. The format is visually
distinct from Sales invoice numbers (`SAL-XXXXXX`) and matches the Blueprint's
specification exactly.

**Alternatives considered**: A separate sequence/counter table — unnecessary complexity
for a single-user app. UUID — not human-readable, doesn't match blueprint spec.

---

### Single Atomic Transaction for Save

**Decision**: `purchases_db.insert_purchase_with_items()` performs the entire save
in one transaction: INSERT into `Purchases`, INSERT N rows into `PurchaseItems`,
UPDATE `Products.stock_quantity` (increment) for each line, UPDATE
`Products.purchase_price` for each line. Commit once at the end; rollback on any
failure.

**Rationale**: Constitution Principle II mandates that multi-step operations touching
more than one table be wrapped in a single transaction. Any partial write (header saved
but stock not updated) would corrupt the system's financial and inventory integrity.

**Alternatives considered**: Separate transactions per table — rejected as a Constitution
violation and a data integrity risk.

---

### `purchase_price` Auto-Update on Save

**Decision**: On every purchase save, each purchased product's `purchase_price` column
in `Products` is updated to the unit price entered on that invoice line (within the
same transaction).

**Rationale**: Blueprint Section 6 (Purchases) explicitly specifies this behavior.
It keeps the product cost data current automatically with zero extra user effort. It
does NOT affect historical profit accuracy because `SaleItems.purchase_price_at_sale`
already freezes the cost at the time of each past sale.

**Alternatives considered**: Not updating `purchase_price` — the Dashboard's Stock
Value calculation and future profit estimates would drift from reality. Tracking full
price history — explicitly out of scope (Blueprint Section 12).

---

### In-Progress Invoice Retained on Page Navigation

**Decision**: The Purchases page widget retains its in-memory state (supplier name,
all added line items, running total, displayed invoice number) when the Admin navigates
to another page and returns. No explicit reset happens on page switch.

**Rationale**: PySide6's `QStackedWidget` keeps all page widgets alive; navigating
away does not destroy them. Leveraging this natural behavior requires zero extra code
and prevents accidental data loss. The Admin must explicitly click "Clear Invoice" or
"Save Invoice" to reset the form. Clarified in spec on 2026-06-27.

**Alternatives considered**: Resetting the form on every `showEvent` — would destroy
in-progress work silently, which violates the Confirmation Dialog Policy (unsaved work
should not be discarded without confirmation).

---

### Product Picker Implementation

**Decision**: Use a `QComboBox` populated via `products_db.get_active_products()` for
the product picker. No custom search widget is needed in Phase 3 — the combo box
provides built-in keyboard navigation and is sufficient for catalogs up to thousands
of entries.

**Rationale**: Blueprint Section 3.7 says "dropdown/search to pick a product". A
`QComboBox` is the canonical PySide6 dropdown that also supports keyboard-based
filtering when the user types (via `setEditable(True)` or the default completer).
This matches Phase 4 (Sales) which uses the same widget type, keeping both picker
implementations identical.

**Alternatives considered**: A `QLineEdit` with a live-search dropdown — more complex
to implement, no additional functional value for the specified use case.

---

### `void_purchase()` Deferred to Phase 5

**Decision**: The `void_purchase()` function in `purchases_db.py` is implemented in
Phase 3 so it is available for Phase 5's Invoice Detail Dialog, but it is NOT exposed
via any UI in Phase 3.

**Rationale**: Implementation Plan Phase 3 scope is purchase invoice creation only.
Voiding is accessed through the Invoice Detail Dialog in Phase 5 (Reports). Implementing
the DB function now (alongside `insert_purchase_with_items`) avoids a second pass
through `purchases_db.py` in Phase 5.

**Stock-sufficiency check for void**: Voiding a purchase requires verifying that
`stock_quantity >= line.quantity` for every line before any update is made. If any
line fails, the entire void is blocked. This validation lives in `purchase_logic.py`
(business rule), not in `purchases_db.py` (raw SQL). Implemented in Phase 3 to keep
`purchase_logic.py` complete for Phase 5's use.

**Alternatives considered**: Implementing void entirely in Phase 5 — would require
reopening `purchases_db.py` and `purchase_logic.py`, violating the bottom-up build
discipline.
