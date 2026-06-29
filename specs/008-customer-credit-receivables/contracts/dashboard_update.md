# Contract: dashboard_page.py & main_window.py Updates

**Layer**: UI | **Feature**: 008-customer-credit-receivables

---

## main_window.py

### Navigation Order Change
Insert "Customers" at index 5, shifting "Reports" to index 6:

```python
nav_buttons = [
    ("Dashboard",  0, "dashboard.svg"),
    ("Products",   1, "products.svg"),
    ("Sales",      2, "sales.svg"),
    ("Purchases",  3, "purchases.svg"),
    ("Expenses",   4, "expenses.svg"),
    ("Customers",  5, "customers.svg"),   # NEW
    ("Reports",    6, "reports.svg"),     # was 5
]
```

A `customers.svg` icon must be added to `ui/icons/`. If unavailable, fall back to no icon (consistent with existing `if os.path.exists` guard).

### Stack Changes
```python
self.customers_page = CustomersPage()
self.stack.addWidget(self.dashboard_page)   # 0
self.stack.addWidget(self.products_page)    # 1
self.stack.addWidget(SalesPage())           # 2
self.stack.addWidget(PurchasesPage())       # 3
self.stack.addWidget(ExpensesPage())        # 4
self.stack.addWidget(self.customers_page)   # 5 NEW
self.stack.addWidget(ReportsPage())         # 6
```

### Signals
- `customers_page.open_customer_detail(customer_id)` → `self._on_open_customer_detail(customer_id)`
  - Creates/reuses a `CustomerDetailPage`, calls `load_customer(customer_id)`, and either:
    - Adds it to the stack temporarily and switches to it, OR
    - Opens it as a top-level `QDialog`-style page
  - Recommended: use a persistent `self.customer_detail_page` added at stack index 7, switched to on demand, with its Back button wired to return to index 5.

- `dashboard_page.navigate_to_customer(customer_id)` → same `_on_open_customer_detail`

---

## dashboard_page.py

### New KPI Cards

Add two cards to the existing KPI grid after the existing four cards:

```
| Total Sales | Total Purchases | Net Profit | [existing 4th] |
| Outstanding Receivables (clickable) | Customers With Balance |
```

Or insert inline with existing cards — exact grid position at implementer discretion, must not break existing layout.

### Outstanding Receivables Card
- Value from `customers_logic.get_outstanding_receivables_total()`
- Wrapped in a clickable container (mousePressEvent or QPushButton styled as card)
- On click: opens `ReceivablesListDialog`
- Emits `navigate_to_customer(customer_id: int)` Signal when user selects a customer from that dialog

### Customers With Balance Card
- Value (count) from `customers_logic.get_customers_with_outstanding_count()`
- Non-interactive display card

### Refresh
Both new cards must be refreshed in the existing `_refresh()` or equivalent method called after payments and after page navigation.
