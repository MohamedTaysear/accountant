# Research: Dashboard & Reports

**Date**: 2026-06-27
**Feature**: 005-dashboard-reports

All decisions below are derived from the existing codebase, the approved Blueprint, the Constitution, and the finalized spec. No external unknowns required external research.

---

## Decision 1: Profit Calculation Source

**Decision**: Always use `SaleItems.purchase_price_at_sale`, never `Products.purchase_price`.

**Rationale**: `purchase_price_at_sale` is written once at save time (`sales_db.py:30–36`) and never updated. It represents the weighted average cost that was current at the moment of the sale. Using it for all historical profit figures — including Dashboard Today's Profit, Total Profit, and Invoice Detail per-line profit — guarantees accuracy even after subsequent purchases change the live WAC.

**Alternatives considered**: Reading `Products.purchase_price` at report time — rejected because it would retroactively distort historical profit figures whenever the purchase price changes.

**SQL formula (canonical)**:
```sql
SUM(si.subtotal)
- SUM(si.quantity * si.purchase_price_at_sale)
- SUM(s.discount_amount)
FROM SaleItems si
JOIN Sales s ON si.sale_id = s.id
WHERE s.status = 'active'
[AND DATE(s.created_at) BETWEEN :start AND :end]
```

---

## Decision 2: Inventory Value and Potential Stock Profit — Scope

**Decision**: Computed across all products (active and inactive). Never stored in the database.

**Rationale**: Inactive products still hold physical stock with real monetary value. Excluding them would understate the true financial position of the inventory. Both values are computed at display time from `Products.purchase_price` (live WAC) and `Products.selling_price`. The Constitution prohibits adding stored columns for derived values that can be computed on the fly.

**Formulas**:
- Inventory Value: `SUM(stock_quantity * purchase_price)` across all Products
- Potential Stock Profit: `SUM((selling_price - purchase_price) * stock_quantity)` across all Products

---

## Decision 3: Date Range Handling

**Decision**: All date filtering uses `DATE(created_at) BETWEEN :start AND :end` with ISO date strings (`YYYY-MM-DD`). Preset ranges are computed in Python at filter-apply time.

**Rationale**: Existing `sales_db.get_all_sales()` and `purchases_db.get_all_purchases()` already use this pattern. Consistency is required — the same approach is used in `report_logic.py`.

**Preset computations** (Python, using `datetime.date`):
- Today: `start = end = date.today()`
- Yesterday: `start = end = date.today() - timedelta(days=1)`
- This Week: `start = date.today() - timedelta(days=date.today().weekday())` (Monday), `end = date.today()`
- This Month: `start = date.today().replace(day=1)`, `end = date.today()`
- Custom Range: values from date picker widgets; validated that start ≤ end before applying

---

## Decision 4: Invoice Detail Dialog — Single Reusable Modal

**Decision**: One `InvoiceDetailDialog` class, parameterized by `invoice_type` (`"sale"` or `"purchase"`) and `invoice_id`. The constructor fetches data and builds the layout conditionally.

**Rationale**: Sales and Purchases share the same modal structure (header, line-items table, action buttons). Conditional rendering of the cost/profit columns and discount footer avoids duplicating the entire dialog for two nearly identical views.

**Sales line-item columns**: Product | Qty | Unit Price | Historical Cost Price | Profit / Line | Subtotal
**Purchases line-item columns**: Product | Qty | Unit Price | Subtotal

**Profit per line formula**: `(unit_price - purchase_price_at_sale) * quantity`

---

## Decision 5: Recent Activity — Data Source

**Decision**: Fetch the 10 most recent rows by `created_at DESC` from both `Sales` and `Purchases` combined, then re-sort and take the top 10 in Python (or via a UNION query).

**Rationale**: SQLite supports `UNION ALL` with `ORDER BY` and `LIMIT`, making this a single query. A Python-side merge is a valid fallback if the union proves complex, but the SQL approach is cleaner and avoids loading unnecessary rows.

**SQL pattern**:
```sql
SELECT invoice_number, 'Sale' AS type, customer_name AS party, total_amount, created_at
FROM Sales
UNION ALL
SELECT invoice_number, 'Purchase' AS type, supplier_name AS party, total_amount, created_at
FROM Purchases
ORDER BY created_at DESC
LIMIT 10
```

---

## Decision 6: Top Products Panels — Data Source

**Decision**: Aggregate from `SaleItems`/`PurchaseItems` joined to active invoices only, filtered by the active date range, grouped by product, ordered by `SUM(quantity) DESC`.

**Rationale**: Voided invoices are excluded from these panels (active only), consistent with the spec (FR-036, FR-037) and the general principle that voided invoices are excluded from all business intelligence totals.

**SQL patterns**:
```sql
-- Top Selling
SELECT p.name, SUM(si.quantity) AS total_qty
FROM SaleItems si
JOIN Sales s ON si.sale_id = s.id
JOIN Products p ON si.product_id = p.id
WHERE s.status = 'active'
[AND DATE(s.created_at) BETWEEN :start AND :end]
GROUP BY si.product_id
ORDER BY total_qty DESC

-- Top Purchased
SELECT p.name, SUM(pi.quantity) AS total_qty
FROM PurchaseItems pi
JOIN Purchases pu ON pi.purchase_id = pu.id
JOIN Products p ON pi.product_id = p.id
WHERE pu.status = 'active'
[AND DATE(pu.created_at) BETWEEN :start AND :end]
GROUP BY pi.product_id
ORDER BY total_qty DESC
```

---

## Decision 7: Low Stock Navigation

**Decision**: The Dashboard Low Stock list emits a signal (or calls a callback) to `main_window.py` when a product row is clicked. `main_window.py` switches to the Products page and calls a method on `products_page.py` to highlight/pre-filter that product by ID.

**Rationale**: The Dashboard must not import or directly control `products_page.py` — that would violate the layering rule (UI files are siblings under `main_window.py`; the shell orchestrates inter-page navigation). The cleanest pattern within the existing architecture is a signal connected in `main_window.py` during setup.

**Implementation approach**: `DashboardPage` emits a `navigate_to_product(product_id: int)` signal. `MainWindow` connects it to a slot that (1) switches the stacked widget to the Products page and (2) calls `products_page.highlight_product(product_id)`. `ProductsPage.highlight_product()` pre-fills the search box with the product name and triggers a search, selecting the matching row.

---

## Decision 8: CSV Export — Active Table Tracking

**Decision**: Track which history table (Sales or Purchases) was last interacted with using a simple instance variable (`self._last_active_table`), updated on any click or focus event on either table.

**Rationale**: Simplest stateful approach compatible with the existing Qt widget pattern. No additional Qt infrastructure needed. Defaults to Sales History if neither has been interacted with yet (safe default since Sales is shown first).

---

## Decision 9: Visual Color Conventions

**Decision**: Use Qt stylesheet strings applied to individual widgets, consistent with the existing pattern in `sales_page.py` (which already uses `setStyleSheet` for the red discount validation border).

**Rationale**: The project uses no CSS framework or theme system — inline `setStyleSheet` is the established pattern. Colors should be chosen to complement the existing Qt default palette without introducing a new design system.

**Color assignments**:
- Profit cards (positive value): green-family success color (e.g. `color: #2e7d32` or similar)
- Low Stock Count card + Low Stock list rows: amber/orange warning color (e.g. `color: #e65100`)
- Error states: red (consistent with existing discount validation)
- Neutral cards: default Qt palette (no override)

---

## Decision 10: report_logic.py — No SQL in Logic Layer

**Decision**: `report_logic.py` calls functions in `sales_db.py` and `purchases_db.py`; it does not write raw SQL itself. New query functions are added to those db files as needed.

**Rationale**: Constitution §I strictly requires the Logic layer to contain no raw SQL. All SQL lives in `*_db.py` files. `report_logic.py` orchestrates calls and performs arithmetic aggregation in Python where the SQL cannot do it cleanly, but never constructs queries.
