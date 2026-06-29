# Data Model: Purchase Invoice Management

**Feature**: 003-purchases
**Date**: 2026-06-27

Phase 3 uses the `Purchases` and `PurchaseItems` tables created in Phase 1 (database.py)
and modifies `Products` rows that were created in Phase 2. No schema changes are needed.
This document records the table contracts and all function signatures the implementer
must honour.

---

## Tables

### Purchases (invoice header — created in Phase 1)

| Column | Type | Constraints | Phase 3 behaviour |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Auto-assigned on insert; used to derive invoice number |
| `invoice_number` | TEXT | UNIQUE NOT NULL | Generated as `PUR-{id:06d}` at save-time |
| `supplier_name` | TEXT | NULLABLE | Optional free-text; stored as-is |
| `total_amount` | REAL | NOT NULL DEFAULT 0 | Sum of all PurchaseItems.subtotal |
| `status` | TEXT | NOT NULL DEFAULT `'active'` | `'active'` on creation; `'voided'` after void |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | Set by DB at insert; not editable |

### PurchaseItems (invoice lines — created in Phase 1)

| Column | Type | Constraints | Phase 3 behaviour |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Auto-assigned |
| `purchase_id` | INTEGER | NOT NULL FK → Purchases(id) | Linked to parent invoice |
| `product_id` | INTEGER | NOT NULL FK → Products(id) | Product purchased |
| `quantity` | REAL | NOT NULL | > 0; decimals allowed |
| `unit_price` | REAL | NOT NULL | ≥ 0; purchase price entered by Admin |
| `subtotal` | REAL | NOT NULL | quantity × unit_price; calculated before insert |

### Products (modified on purchase save — created in Phase 2)

| Column | Modified? | How |
|---|---|---|
| `stock_quantity` | **Yes** | Incremented by `quantity` per PurchaseItems row, within the same transaction |
| `purchase_price` | **Yes** | Overwritten with `unit_price` per PurchaseItems row, within the same transaction |
| All other columns | No | Not touched during purchase save |

---

## Invoice Number Generation

```
invoice_number = f"PUR-{purchase_id:06d}"
```

- `purchase_id` is the `lastrowid` returned after INSERT INTO Purchases.
- The **preview** shown on the form before saving is computed as
  `f"PUR-{MAX(id)+1:06d}"` (or `f"PUR-000001"` when the table is empty).
- The actual stored number uses `lastrowid` to guarantee uniqueness even if rows
  were deleted (which never happens — invoices are voided, not deleted — but
  using `lastrowid` is more robust than COUNT).

---

## Invoice Status Lifecycle

```
[Insert]  →  status = 'active'
                  │
              Void (Phase 5 only)
                  │
              status = 'voided'   ← terminal; cannot be undone
```

A voided purchase is never deleted. It remains in the `Purchases` table permanently
for audit purposes.

---

## `purchases_db.py` Function Signatures

```python
def insert_purchase_with_items(
    supplier_name: str | None,
    items: list[dict]   # each dict: {product_id, quantity, unit_price, subtotal}
) -> str:
    """
    Single atomic transaction:
      1. INSERT INTO Purchases (supplier_name, total_amount, status)
         VALUES (?, ?, 'active')
         — total_amount = sum(item['subtotal'] for item in items)
      2. Use conn.lastrowid as purchase_id
      3. Generate invoice_number = f"PUR-{purchase_id:06d}"
      4. UPDATE Purchases SET invoice_number = ? WHERE id = ?
      5. For each item:
           INSERT INTO PurchaseItems (purchase_id, product_id, quantity, unit_price, subtotal)
           UPDATE Products SET
             stock_quantity = stock_quantity + ?,
             purchase_price = ?
           WHERE id = ?
      6. conn.commit()
    Returns the generated invoice_number string.
    Raises Exception on any failure (caller should rollback implicitly via conn.close
    without commit, or use explicit rollback).
    """

def get_purchase_by_id(purchase_id: int) -> sqlite3.Row | None:
    """
    SELECT * FROM Purchases WHERE id = ?
    Returns single row or None.
    Used by Invoice Detail Dialog (Phase 5).
    """

def get_purchase_items(purchase_id: int) -> list[sqlite3.Row]:
    """
    SELECT pi.*, p.name AS product_name
    FROM PurchaseItems pi
    JOIN Products p ON pi.product_id = p.id
    WHERE pi.purchase_id = ?
    Returns all line items for the invoice with product names.
    Used by Invoice Detail Dialog (Phase 5).
    """

def get_all_purchases(
    start_date: str | None = None,
    end_date: str | None = None
) -> list[sqlite3.Row]:
    """
    SELECT * FROM Purchases
    [WHERE created_at BETWEEN ? AND ?]
    ORDER BY created_at DESC
    Returns all purchases (active and voided) optionally filtered by date range.
    Date strings in 'YYYY-MM-DD' format.
    Used by Reports page (Phase 5).
    """

def void_purchase(purchase_id: int) -> None:
    """
    MUST be called only after purchase_logic.check_void_stock() passes for all items.
    Single atomic transaction:
      1. UPDATE Purchases SET status = 'voided' WHERE id = ?
      2. For each PurchaseItems row WHERE purchase_id = ?:
           UPDATE Products SET stock_quantity = stock_quantity - quantity WHERE id = ?
      3. conn.commit()
    Raises Exception on failure.
    Used by Invoice Detail Dialog (Phase 5). Implemented here to keep purchases_db.py
    complete; not called from any Phase 3 UI.
    """
```

---

## `logic/purchase_logic.py` Function Signatures

```python
# In-memory line item type (plain dict, not a class):
# {
#   "product_id": int,
#   "product_name": str,
#   "quantity": float,
#   "unit_price": float,
#   "subtotal": float     # quantity * unit_price, calculated by add_line()
# }

def validate_line(quantity: float, unit_price: float) -> tuple[bool, str]:
    """
    Returns (True, "") if valid.
    Returns (False, error_message) if:
      - quantity <= 0  →  "Quantity must be greater than 0."
      - unit_price < 0 →  "Unit price cannot be negative."
    """

def calculate_total(items: list[dict]) -> float:
    """
    Returns sum(item['subtotal'] for item in items).
    Returns 0.0 if items is empty.
    """

def save_purchase(
    supplier_name: str | None,
    items: list[dict]
) -> str:
    """
    Validates: len(items) >= 1 (raises ValueError if not).
    Calls purchases_db.insert_purchase_with_items(supplier_name, items).
    Returns the generated invoice_number string.
    Raises ValueError for business rule violations.
    Raises Exception for database errors (caller catches and shows QMessageBox).
    """

def check_void_stock(purchase_id: int) -> tuple[bool, str]:
    """
    For each PurchaseItems row for this purchase_id:
      SELECT stock_quantity FROM Products WHERE id = product_id
      If stock_quantity < item.quantity → return (False, "Cannot void: some of
        this stock has already been sold. [Product: {name}]")
    If all lines pass → return (True, "")
    Used by Invoice Detail Dialog (Phase 5) before calling purchases_db.void_purchase().
    """

def void_purchase(purchase_id: int) -> None:
    """
    Calls check_void_stock() first; raises ValueError if it fails.
    Then calls purchases_db.void_purchase(purchase_id).
    Raises ValueError for business rule violations, Exception for DB errors.
    Used by Invoice Detail Dialog (Phase 5).
    """

def get_next_invoice_number() -> str:
    """
    SELECT MAX(id) FROM Purchases
    Returns f"PUR-{(max_id or 0) + 1:06d}"
    Used to display the preview invoice number on the Purchases form.
    """
```

---

## Validation Rules (enforced in `purchase_logic.py` before any DB call)

| Field | Rule | Error Message |
|---|---|---|
| Line quantity | Numeric; > 0 | "Quantity must be greater than 0." |
| Line unit price | Numeric; ≥ 0 | "Unit price cannot be negative." |
| Invoice lines | At least 1 line required before save | "Invoice must have at least one item before saving." |
| Void stock check | `stock_quantity >= quantity` for all lines | "Cannot void: some of this stock has already been sold." |

Supplier name: optional free text, no validation rules.
