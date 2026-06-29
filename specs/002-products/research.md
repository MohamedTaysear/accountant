# Research: Product Catalog Management

**Feature**: 002-products
**Date**: 2026-06-27
**Status**: Complete — all decisions pre-made in `BLUEPRINT.md`

No open unknowns existed at planning time. This document records the rationale for
each key technical decision.

---

## Decision Log

### No Logic Layer for Product CRUD

**Decision**: `products_db.py` (data access) and `ui/products_page.py` /
`ui/product_dialog.py` (UI) with no `logic/products_logic.py` intermediate file.

**Rationale**: Constitution Principle I requires a logic layer only when business rules
cannot live cleanly in either the data access or UI layer. Product CRUD has:
- No multi-table transactions (add/edit/delete touch only `Products`; the `SaleItems`/
  `PurchaseItems` reference check is a read-only query, not a write transaction).
- No calculated fields (no subtotals, no stock arithmetic).
- No voiding or reversal rules.
Input validation belongs in `product_dialog.py` (UI — before the DB call); the delete
guard and active filter belong in `products_db.py` (data access — pure SQL queries).

**Alternatives considered**: Adding `logic/products_logic.py` as a pass-through layer —
rejected as unnecessary complexity with no benefit. Constitution Principle II ("no
formal repository-pattern abstraction beyond the plain per-table `*_db.py` files")
confirms this.

---

### SKU Uniqueness Enforcement Strategy

**Decision**: Rely on the SQLite `UNIQUE` constraint on the `sku` column (already
created in Phase 1) and catch the resulting `sqlite3.IntegrityError` in the dialog's
save handler, translating it into a friendly "SKU already in use" message.

**Rationale**: The constraint is already in the schema. A pre-check query before
insert/update would introduce a TOCTOU race (not a practical concern for a
single-user app, but still unnecessary code). Catching `IntegrityError` and inspecting
the error message string to distinguish SKU violations from other integrity errors is
the cleanest stdlib approach.

**Alternatives considered**: Pre-check `SELECT id FROM Products WHERE sku = ?` before
insert — adds a round-trip and requires a separate function. Rejected in favour of the
exception-catch pattern.

---

### Delete vs Deactivate Decision Point

**Decision**: `products_db.is_product_referenced(product_id) -> bool` runs
`SELECT 1 FROM SaleItems WHERE product_id = ? UNION SELECT 1 FROM PurchaseItems WHERE product_id = ? LIMIT 1`
and returns `True` if any row is found. The Products page calls this before deciding
whether to show a Delete or Deactivate button for each row.

**Rationale**: Blueprint Section 6 specifies this rule exactly. The query is cheap
(indexed foreign keys), returns at most one row, and is the canonical guard for all
permanent-delete attempts. No caching needed for a single-user app where the catalog
is never thousands of rows.

**Alternatives considered**: Checking only `SaleItems` — rejected; Blueprint
explicitly requires both tables. Storing a `has_history` flag on the Product row —
rejected as denormalization that can go stale.

---

### Single Shared `get_active_products()` Function

**Decision**: `products_db.get_active_products() -> list[sqlite3.Row]` is the sole
function that returns products for any picker (Sales page in Phase 4, Purchases page
in Phase 3). It executes `SELECT ... FROM Products WHERE is_active = 1 ORDER BY name`.

**Rationale**: Constitution Principle IV explicitly mandates "exactly one shared
function for fetching active products, reused by both screens." Having two separate
functions (one per screen) risks divergence in the future and contradicts the
"single global rule" intent. Implemented in Phase 2 and called unchanged in Phases 3
and 4.

**Alternatives considered**: Per-screen functions — rejected by Constitution.

---

### Search Implementation

**Decision**: Live filter using `LIKE` SQL pattern matching:
`WHERE (name LIKE ? OR sku LIKE ?) AND is_active = ?` where the pattern is
`'%' + search_text + '%'`. The query runs on every `textChanged` signal from the
search `QLineEdit`. Results replace the table contents directly.

**Rationale**: Blueprint Section 3.4 specifies "filters by name or SKU as you type
or on Enter." For a local SQLite database with a catalog that will never exceed
thousands of rows, a live SQL query per keystroke is fast enough (sub-millisecond)
and simpler than maintaining an in-memory filtered list.

**Alternatives considered**: Load all products into memory and filter in Python —
adds unnecessary state; rejected. Debounce the search input — unnecessary at this
scale; rejected.

---

### Selling Price Warning Behaviour

**Decision**: When `selling_price < purchase_price`, show a `QMessageBox.question`
(Yes/No) with the message "Selling price is less than purchase price. Save anyway?"
before proceeding with the save. If user clicks Yes, save proceeds; if No, the dialog
stays open.

**Rationale**: Blueprint Section 7 says "Warn, but don't block, if selling price <
purchase price." A Yes/No confirmation gives the user a meaningful decision point
without hard-blocking a legitimate business choice (e.g., a clearance sale item).

**Alternatives considered**: Non-blocking `QMessageBox.warning` shown after save —
too late, user can't reconsider. Inline label warning below the field — requires
more UI layout complexity for a rare edge case. Rejected both.
