# Contract: ui/dashboard_page.py

**Layer**: UI (PySide6 only — no sqlite3, no raw SQL)
**Depends on**: `logic/report_logic`, `products_db`
**Signals emitted**: `navigate_to_product(int)` — connected by `main_window.py`

---

## Class: DashboardPage(QWidget)

### Signals
```python
navigate_to_product = Signal(int)   # emitted with product_id when Low Stock row is clicked
```

### Public Methods
```python
def __init__(self, parent=None): ...
def showEvent(self, event): ...     # refreshes all data every time page becomes visible
```

### Layout (top to bottom)

1. **Summary Cards row(s)** — 10 cards in display order:
   - Total Products | Active Products | Inactive Products
   - Inventory Value | Potential Stock Profit
   - Today's Sales | Today's Purchases | Today's Profit | Total Profit
   - Low Stock Count

2. **Low Stock list** (QTableWidget, read-only):
   - Columns: Name, Category, Current Stock, Reorder Level
   - Active products only (`stock_quantity ≤ reorder_level`)
   - Row click → emits `navigate_to_product(product_id)`
   - Warning color applied to rows and the Low Stock Count card
   - Hidden or shows empty-state text when no qualifying products

3. **Recent Activity table** (QTableWidget, read-only):
   - Columns: Invoice Number, Type, Date, Customer/Supplier, Total Amount
   - 10 most recent invoices (Sales + Purchases combined), newest first
   - No row interaction required (read-only display)

### Color Rules
| Element | Condition | Style |
|---|---|---|
| Today's Profit card | value > 0 | success/green color |
| Total Profit card | value > 0 | success/green color |
| Low Stock Count card | always | warning/amber color |
| Low Stock list rows | always | warning/amber color |
| All other cards | always | default Qt palette |

### Data Flow
```
showEvent()
  → report_logic.get_total_sales(today, today)         → Today's Sales card
  → report_logic.get_total_purchases(today, today)      → Today's Purchases card
  → report_logic.get_total_profit(today, today)         → Today's Profit card
  → report_logic.get_total_profit()                     → Total Profit card
  → report_logic.get_inventory_value()                  → Inventory Value card
  → report_logic.get_potential_stock_profit()           → Potential Stock Profit card
  → report_logic.get_low_stock_count()                  → Low Stock Count card
  → products_db.get_low_stock_products()                → Low Stock list
  → report_logic.get_recent_activity(limit=10)          → Recent Activity table
  → products_db counts (active/inactive/total)          → product count cards
```
