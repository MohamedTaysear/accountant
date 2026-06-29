# Contract: logic/report_logic.py

**Layer**: Logic (no SQL, no PySide6 imports)
**Depends on**: `sales_db`, `purchases_db`
**Called by**: `ui/dashboard_page.py`, `ui/reports_page.py`

---

## Functions

### get_total_sales(start_date=None, end_date=None) → float
Returns the sum of `total_amount` for all **active** Sales invoices.
- `start_date`, `end_date`: ISO date strings `"YYYY-MM-DD"`, both optional.
- If omitted: All Time.
- Returns `0.0` if no matching rows.

### get_total_purchases(start_date=None, end_date=None) → float
Returns the sum of `total_amount` for all **active** Purchases invoices.
- Same date parameters as above.

### get_total_profit(start_date=None, end_date=None) → float
Returns total profit for active sales within the date range.

**Formula**:
```
SUM(SaleItems.subtotal)
- SUM(SaleItems.quantity × SaleItems.purchase_price_at_sale)
- SUM(Sales.discount_amount)
```

- Only active Sales/SaleItems are included.
- `Products.purchase_price` is **never** read by this function.
- Returns `0.0` if no matching rows.

### get_recent_activity(limit=10) → list[dict]
Returns the `limit` most recent invoices across Sales and Purchases combined, ordered by `created_at DESC`.

Each dict contains:
```python
{
    "invoice_number": str,
    "type": "Sale" | "Purchase",
    "party": str | None,       # customer_name for Sales, supplier_name for Purchases
    "total_amount": float,
    "created_at": str          # ISO timestamp string
}
```

### get_top_selling_products(start_date=None, end_date=None) → list[dict]
Returns products ranked by total quantity sold (active invoices only, within date range).

Each dict:
```python
{"product_name": str, "total_quantity": float}
```
Ordered descending by `total_quantity`.

### get_top_purchased_products(start_date=None, end_date=None) → list[dict]
Same pattern as above but for Purchases/PurchaseItems.

### get_inventory_value() → float
Returns `SUM(stock_quantity × purchase_price)` across **all** products (active and inactive).

### get_potential_stock_profit() → float
Returns `SUM((selling_price − purchase_price) × stock_quantity)` across **all** products.

### get_low_stock_count() → int
Returns count of active products where `stock_quantity ≤ reorder_level`.
