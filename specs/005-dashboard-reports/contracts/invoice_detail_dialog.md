# Contract: ui/invoice_detail_dialog.py

**Layer**: UI (PySide6 only)
**Depends on**: `sales_db`, `purchases_db`, `logic/sales_logic`, `logic/purchase_logic`
**Opened by**: `ui/reports_page.py` (double-click on history row)

---

## Class: InvoiceDetailDialog(QDialog)

### Constructor
```python
def __init__(self, invoice_type: str, invoice_id: int, parent=None):
    # invoice_type: "sale" or "purchase"
    # invoice_id: integer primary key
```

### Behavior by Invoice Type

#### Sale Invoice
Displays:
- Header: Invoice Number, Date, Status, Customer Name (blank if None)
- Line-items table columns: **Product | Qty | Unit Price | Historical Cost Price | Profit / Line | Subtotal**
  - Historical Cost Price = `SaleItems.purchase_price_at_sale` (read directly — never from `Products.purchase_price`)
  - Profit / Line = `(unit_price − purchase_price_at_sale) × quantity` (computed at display time, never stored)
- Footer: Subtotal (sum of line subtotals) → Discount → Grand Total

#### Purchase Invoice
Displays:
- Header: Invoice Number, Date, Status, Supplier Name (blank if None)
- Line-items table columns: Product | Qty | Unit Price | Subtotal
- Footer: Grand Total only (no discount row; no cost/profit columns)

### Buttons

| Button | Enabled when | Action |
|---|---|---|
| Void Invoice | `status == 'active'` | Shows confirmation → calls void logic → refreshes dialog status |
| Print | Always | Opens `QPrintDialog`; prints visible dialog content |
| Close | Always | Closes dialog; caller refreshes Reports page |

### Void Logic
- **Sale**: calls `sales_logic.void_sale(invoice_id)` — single transaction; stock restored.
- **Purchase**: calls `purchase_logic.void_purchase(invoice_id)` — pre-checks stock sufficiency for all lines; blocks with error message if any line fails; otherwise proceeds as single transaction.
- After successful void: Void button disabled, status label updated to "Voided".
- On any error: friendly `QMessageBox` — no raw traceback.

### Wait Cursor
Applied during Void and Print operations via `QApplication.setOverrideCursor(Qt.WaitCursor)` / `restoreOverrideCursor()`.
