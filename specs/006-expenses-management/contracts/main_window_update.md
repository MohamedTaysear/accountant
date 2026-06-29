# Contract: MainWindow Update

**File**: `accounting_system/ui/main_window.py` (existing, modified)
**Layer**: UI

---

## Sidebar Navigation Changes

Two new buttons added to the nav_buttons list:

```python
nav_buttons = [
    ("Dashboard",        0),
    ("Products",         1),
    ("Sales",            2),
    ("Purchases",        3),
    ("Reports",          4),
    ("Expenses",         5),   # NEW
    ("Expenses Report",  6),   # NEW
]
```

---

## Page Stack Changes

```python
from ui.expenses_page        import ExpensesPage
from ui.expenses_report_page import ExpensesReportPage

self.stack.addWidget(ExpensesPage())         # 5
self.stack.addWidget(ExpensesReportPage())   # 6
```

No changes to existing page indices 0–4.
