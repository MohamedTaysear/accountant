# Data Model: Product Catalog Management

**Feature**: 002-products
**Date**: 2026-06-27

Phase 2 uses the `Products` table created in Phase 1. No schema changes are needed.
This document records the table contract and all `products_db.py` function signatures
the implementer must honour.

---

## Products Table (created in Phase 1, used fully from Phase 2)

| Column | Type | Constraints | Phase 2 behaviour |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Auto-assigned on insert |
| `name` | TEXT | NOT NULL | Required; max 100 chars validated in UI |
| `sku` | TEXT | UNIQUE, NULLABLE | Optional; duplicate non-null → `IntegrityError` |
| `unit` | TEXT | NOT NULL DEFAULT `'pcs'` | Defaults to `"pcs"` if field left blank |
| `purchase_price` | REAL | NOT NULL DEFAULT `0` | ≥ 0 validated in UI |
| `selling_price` | REAL | NOT NULL DEFAULT `0` | ≥ 0 validated; warning if < purchase_price |
| `stock_quantity` | REAL | NOT NULL DEFAULT `0` | ≥ 0; decimals allowed |
| `reorder_level` | REAL | NOT NULL DEFAULT `5` | ≥ 0; decimals allowed |
| `is_active` | INTEGER | NOT NULL DEFAULT `1` | 1 = active, 0 = deactivated |

**SKU uniqueness note**: SQLite's `UNIQUE` constraint allows multiple NULL values, so
products without a SKU coexist freely. Only duplicate non-null SKUs are rejected.

---

## Active/Inactive Lifecycle

```
[Created]  →  is_active = 1  (active)
                  │
          Deactivate (only if referenced in SaleItems or PurchaseItems)
                  │
              is_active = 0  (inactive)
                  │
              Activate
                  │
              is_active = 1  (active)

[Delete]  ── only allowed when is_product_referenced() returns False
```

**Rules**:
- A product starts active (`is_active = 1`) on creation.
- If it has never appeared in any `SaleItems` or `PurchaseItems` row → Delete is
  offered (permanent removal).
- If it HAS appeared in any invoice row → Deactivate is offered instead.
- Deactivation is reversible (Activate restores `is_active = 1`).
- An inactive product is hidden from: Products table default view, Sales product
  picker (Phase 4), Purchases product picker (Phase 3) — all use `get_active_products()`.

---

## `products_db.py` Function Signatures

```python
def insert_product(
    name: str,
    sku: str | None,
    unit: str,
    purchase_price: float,
    selling_price: float,
    stock_quantity: float,
    reorder_level: float
) -> None:
    """
    INSERT INTO Products (...) VALUES (?, ?, ?, ?, ?, ?, ?)
    is_active defaults to 1.
    Raises sqlite3.IntegrityError if sku is non-null and already exists.
    """

def update_product(
    product_id: int,
    name: str,
    sku: str | None,
    unit: str,
    purchase_price: float,
    selling_price: float,
    stock_quantity: float,
    reorder_level: float
) -> None:
    """
    UPDATE Products SET ... WHERE id = ?
    Raises sqlite3.IntegrityError if sku conflicts with another product's non-null sku.
    """

def delete_product(product_id: int) -> None:
    """
    DELETE FROM Products WHERE id = ?
    Caller MUST check is_product_referenced() first; this function does not guard itself.
    """

def set_active(product_id: int, is_active: int) -> None:
    """
    UPDATE Products SET is_active = ? WHERE id = ?
    Pass 0 to deactivate, 1 to activate.
    """

def search_products(search_text: str, include_inactive: bool) -> list[sqlite3.Row]:
    """
    SELECT * FROM Products
    WHERE (name LIKE '%?%' OR sku LIKE '%?%')
      [AND is_active = 1 if not include_inactive]
    ORDER BY name
    Returns all columns. Empty search_text returns all products (matching filter).
    """

def get_active_products() -> list[sqlite3.Row]:
    """
    SELECT id, name, unit, selling_price, stock_quantity
    FROM Products WHERE is_active = 1 ORDER BY name
    THE single shared function for all product pickers (Sales + Purchases).
    """

def get_low_stock_products() -> list[sqlite3.Row]:
    """
    SELECT id, name, stock_quantity, reorder_level
    FROM Products WHERE is_active = 1 AND stock_quantity <= reorder_level
    ORDER BY name
    Used by Dashboard page in Phase 5. Implemented now so the function exists.
    """

def is_product_referenced(product_id: int) -> bool:
    """
    SELECT 1 FROM SaleItems   WHERE product_id = ? LIMIT 1
    UNION
    SELECT 1 FROM PurchaseItems WHERE product_id = ? LIMIT 1
    Returns True if any row found (product has invoice history).
    """

def get_product_by_id(product_id: int) -> sqlite3.Row | None:
    """
    SELECT * FROM Products WHERE id = ?
    Returns the single row or None. Used to pre-fill the Edit dialog.
    """
```

---

## `ui/product_dialog.py` Validation Rules

These are the validation rules the dialog MUST enforce before calling any
`products_db` function:

| Field | Rule | Error Message |
|---|---|---|
| Name | Non-empty after strip; ≤ 100 chars | "Product name is required." |
| Purchase Price | Numeric; ≥ 0 | "Purchase price must be 0 or greater." |
| Selling Price | Numeric; ≥ 0 | "Selling price must be 0 or greater." |
| Selling Price | If < Purchase Price | QMessageBox.question "Selling price is less than purchase price. Save anyway?" (Yes/No) |
| Stock Quantity | Numeric; ≥ 0; decimals OK | "Stock quantity must be 0 or greater." |
| Reorder Level | Numeric; ≥ 0; decimals OK | "Reorder level must be 0 or greater." |
| SKU (IntegrityError) | Raised by DB on duplicate non-null SKU | "SKU already in use. Please enter a unique SKU or leave it blank." |

Unit field: if blank, default to `"pcs"` before saving (no error).
SKU field: if blank, pass `None` to `products_db` (not an empty string).
