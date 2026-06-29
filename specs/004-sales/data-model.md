# Data Model: Phase 4 — Sales

**Date**: 2026-06-27
**Status**: No schema changes — all tables created in Phase 1.

---

## Entities

### Sales (invoice header)

Already defined in `database.py`. Reproduced here for reference.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Used to derive `invoice_number` via `lastrowid` |
| invoice_number | TEXT | UNIQUE NOT NULL | Format: `SAL-NNNNNN` (e.g. `SAL-000001`) |
| customer_name | TEXT | NULLABLE | Optional; stored as NULL when empty |
| discount_amount | REAL | NOT NULL, DEFAULT 0 | Invoice-level discount; ≥ 0; must not exceed sum of line subtotals |
| total_amount | REAL | NOT NULL, DEFAULT 0 | Grand Total = sum of SaleItems subtotals − discount_amount |
| status | TEXT | NOT NULL, DEFAULT 'active' | Values: `'active'` or `'voided'` (void implemented in Phase 5) |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | Auto-set by SQLite |

**Invariants**:
- `total_amount` = (Σ `SaleItems.subtotal`) − `discount_amount`. Never negative.
- `discount_amount` ≤ Σ `SaleItems.subtotal` (enforced in logic layer before save).
- `invoice_number` is globally unique; derived from `id` immediately after INSERT via `lastrowid`.
- Once saved, a Sales row is never updated (except `status` set to `'voided'` in Phase 5).

---

### SaleItems (invoice lines)

Already defined in `database.py`. Reproduced here for reference.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| sale_id | INTEGER | NOT NULL, FK → Sales(id) | Set to the new `Sales.id` from `lastrowid` |
| product_id | INTEGER | NOT NULL, FK → Products(id) | The sold product |
| quantity | REAL | NOT NULL | Decimal allowed (e.g. 2.5); > 0 |
| unit_price | REAL | NOT NULL | Product's `selling_price` at the time the line was added to the in-progress invoice |
| purchase_price_at_sale | REAL | NOT NULL | Product's `purchase_price` at the moment of the DB save (captured in the save transaction) |
| subtotal | REAL | NOT NULL | = `quantity × unit_price` (pre-discount; discount is at invoice level only) |

**Invariants**:
- `quantity` > 0 (enforced before line-add).
- `unit_price` is the product's `selling_price` at line-add time — not user-editable on the Sales page.
- `purchase_price_at_sale` is read from `Products.purchase_price` at save-time (not line-add time).
- `subtotal` = `quantity × unit_price` (computed in logic layer, stored for audit history).
- One or more SaleItems rows must exist per Sales row (enforced before save).

---

### Products (updated on save)

No structural changes. Phase 4 only writes to `stock_quantity`:

| Column | Updated on Sale Save? | How |
|---|---|---|
| stock_quantity | **YES** | Decremented by `quantity` for each SaleItems line in the same transaction |
| purchase_price | No | Not touched by Sales (only updated by Purchases, Phase 3) |
| All other columns | No | Read-only from the perspective of this phase |

---

## State Transitions

### Sales.status

```
[not yet created]
       │  Save Invoice
       ▼
   'active'
       │  Void Invoice (Phase 5)
       ▼
   'voided'   ──── (terminal, no further transitions)
```

Phase 4 only implements the transition to `'active'`. The `'voided'` transition is Phase 5.

---

## In-Memory Invoice Structure (UI layer — not persisted until save)

The in-progress invoice is held in `sales_page.py` as a Python list `_items`. Each entry is a dict:

```
{
  "product_id":   int,    # Products.id
  "product_name": str,    # display only
  "quantity":     float,  # user-entered
  "unit_price":   float,  # Products.selling_price at line-add time
  "subtotal":     float,  # quantity × unit_price
}
```

`purchase_price_at_sale` is NOT stored in this dict — it is fetched from `Products.purchase_price` during the DB save transaction.

---

## Relationships

```
Sales (1) ──────────── (many) SaleItems
                               │
                               └── product_id → Products(id)
```

- `Products` is read at line-add time (for `selling_price`, `stock_quantity`, `name`) and at save-time (for `purchase_price_at_sale`).
- `Products.stock_quantity` is decremented per line within the same save transaction.

---

## Validation Rules (enforced in logic layer)

| Field | Rule | Enforced At |
|---|---|---|
| quantity (line) | > 0 | Before line-add |
| quantity (line) | ≤ effective available stock (DB stock − already-queued for same product) | Before line-add |
| discount_amount | ≥ 0 | Before save |
| discount_amount | ≤ Σ SaleItems subtotals | Before save (also real-time UI clamp) |
| invoice lines | count ≥ 1 | Before save |
| customer_name | any string or NULL | No format validation |
