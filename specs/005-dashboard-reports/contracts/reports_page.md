# Contract: ui/reports_page.py

**Layer**: UI (PySide6 only)
**Depends on**: `logic/report_logic`, `ui/invoice_detail_dialog`
**Opened by**: `ui/main_window.py` (sidebar navigation)

---

## Class: ReportsPage(QWidget)

### Public Methods
```python
def __init__(self, parent=None): ...
def showEvent(self, event): ...   # applies current filter on page show
```

### Layout (top to bottom)

1. **Date Filter bar**
   - QComboBox with options: Today | Yesterday | This Week | This Month | Custom Range
   - Two QDateEdit pickers (enabled only when Custom Range is selected; disabled otherwise)
   - "Apply" button (enabled only when Custom Range is selected)
   - Selecting any preset immediately triggers `_apply_filter()` — no Apply click needed

2. **Summary blocks** (3 read-only labels): Total Sales | Total Purchases | Total Profit

3. **History tables** (side by side or stacked):
   - Sales History: Invoice Number, Date, Customer, Total Amount, Status — sorted newest first
   - Purchases History: Invoice Number, Date, Supplier, Total Amount, Status — sorted newest first
   - Double-click on any row → opens `InvoiceDetailDialog`, then calls `_apply_filter()` on close

4. **Top Products panels** (2 read-only tables, below history):
   - Top Selling Products: Product Name, Total Qty Sold — descending
   - Top Purchased Products: Product Name, Total Qty Purchased — descending
   - Both respect the active date filter

5. **"Export to CSV" button** (bottom bar)
   - Exports the last-interacted-with history table (Sales or Purchases)
   - Default: Sales History if neither has been interacted with
   - Opens QFileDialog (save); writes via Python `csv` module; wait cursor during write

### Date Preset Logic (Python, applied in `_apply_filter`)

```python
from datetime import date, timedelta

def _get_date_range(self):
    preset = self.filter_combo.currentText()
    today = date.today()
    if preset == "Today":
        return str(today), str(today)
    elif preset == "Yesterday":
        y = today - timedelta(days=1)
        return str(y), str(y)
    elif preset == "This Week":
        start = today - timedelta(days=today.weekday())  # Monday
        return str(start), str(today)
    elif preset == "This Month":
        return str(today.replace(day=1)), str(today)
    elif preset == "Custom Range":
        start = self.from_date.date().toPython()
        end = self.to_date.date().toPython()
        if start > end:
            # show validation error, return None
            return None
        return str(start), str(end)
```

### Active Table Tracking (for CSV export)

```python
self._last_active_table = "sales"   # default

# Connect to both tables:
self.sales_table.clicked.connect(lambda: setattr(self, '_last_active_table', 'sales'))
self.purchases_table.clicked.connect(lambda: setattr(self, '_last_active_table', 'purchases'))
```

### Data Flow on `_apply_filter()`
```
_get_date_range() → (start, end)
  → report_logic.get_total_sales(start, end)            → Total Sales label
  → report_logic.get_total_purchases(start, end)        → Total Purchases label
  → report_logic.get_total_profit(start, end)           → Total Profit label
  → sales_db.get_all_sales(start, end)                  → Sales History table
  → purchases_db.get_all_purchases(start, end)          → Purchases History table
  → report_logic.get_top_selling_products(start, end)   → Top Selling panel
  → report_logic.get_top_purchased_products(start, end) → Top Purchased panel
```
