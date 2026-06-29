# Contract: DashboardPage Update

**File**: `accounting_system/ui/dashboard_page.py` (existing, modified)
**Layer**: UI

---

## New Cards

Three new `QLabel` cards added to the existing `QGridLayout` in `_build_ui()`:

| Card Title | Label attr | Grid position |
|------------|-----------|---------------|
| "Today's Expenses" | `self.lbl_today_expenses` | Row 2, Col 1 |
| "This Month Expenses" | `self.lbl_this_month_expenses` | Row 2, Col 2 |
| "Net Profit" | `self.lbl_net_profit` | Row 2, Col 3 |

The existing "Low Stock Count" card (currently at Row 2, Col 0) stays at Row 2, Col 0.

---

## _refresh() Additions

```python
today_expenses      = report_logic.get_today_expenses()
this_month_expenses = report_logic.get_this_month_expenses()
net_profit          = report_logic.get_net_profit()

self.lbl_today_expenses.setText(f"{today_expenses:,.2f}")
self.lbl_this_month_expenses.setText(f"{this_month_expenses:,.2f}")
self.lbl_net_profit.setText(f"{net_profit:,.2f}")
```

Color for Net Profit card:
- Positive: green `#2e7d32` (same as profit cards)
- Zero or negative: default bold (no special color)

---

## Existing Cards — No Changes

The existing `lbl_today_profit`, `lbl_this_month_profit`, `lbl_total_profit` cards and their calculations are untouched.

---

## Trigger for Refresh

The Dashboard already refreshes on `showEvent`. No additional refresh trigger is needed — navigating back to the Dashboard after any expense change will show updated values. (The spec requires dashboard updates "whenever an expense is added, edited, or deleted"; since the Expenses page and Dashboard are in the same `QStackedWidget`, switching back to Dashboard triggers `showEvent` → `_refresh()`.)
