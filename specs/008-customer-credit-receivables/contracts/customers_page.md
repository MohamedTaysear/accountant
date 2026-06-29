# Contract: UI Pages & Dialogs

**Layer**: UI | **Feature**: 008-customer-credit-receivables

All UI files MUST import only from `logic/` modules. No direct `*_db.py` imports.

---

## customers_page.py — CustomersPage(QWidget)

**Navigation**: index 5 (after Expenses=4, before Reports=6)

### Layout
- Page title: "Customers"
- Search bar (QLineEdit, real-time name filter)
- Toggle button: "Show With Balance Only"
- QTableWidget columns: Customer Name | Phone | Invoices | Total Purchases | Outstanding Balance
- Rows with `outstanding_balance > 0` highlighted (accent color on text/row)
- Double-clicking a row emits `open_customer_detail(customer_id)`

### Signals
- `open_customer_detail(customer_id: int)`

### Public methods
- `_refresh()` — reloads from `customers_logic.get_customers_list()`

---

## customer_detail_page.py — CustomerDetailPage(QWidget)

### Layout
- Back button → emits `back_requested` signal
- Customer name (page title), phone (subtitle)
- "Receive Payment" button — visible only when `outstanding_balance > 0`
- Four summary cards: Outstanding Balance | Total Purchases | Total Paid | Number of Invoices
- QTabWidget with two tabs:
  - **Invoices** tab: Invoice # | Date | Total | Paid | Remaining | Status
    - Status column color-coded: Paid=green, Partially Paid=orange, Unpaid=red, Voided=gray
  - **Payment History** tab: Date | Invoice # | Amount | Remaining After | Notes
    - Includes invoice number for each payment (from `Payments.sale_id → Sales.invoice_number`)

### Signals
- `back_requested` — emitted by back button

### Public methods
- `load_customer(customer_id: int)` — called by MainWindow; sets `self._customer_id` and calls `_refresh()`
- `_refresh()` — reloads from `customers_logic.get_customer_profile(customer_id)`

### Receive Payment flow
Clicking "Receive Payment" opens `ReceivePaymentDialog`. On dialog `accept()`, calls `self._refresh()`.

---

## receive_payment_dialog.py — ReceivePaymentDialog(QDialog)

### Constructor
`__init__(customer_id: int, customer_name: str, parent=None)`

The dialog fetches outstanding invoices internally via `customers_logic.get_outstanding_invoices_for_customer(customer_id)` on open.

### Layout
1. **Outstanding Invoices selector**: QComboBox listing each outstanding invoice as:
   `"SAL-000042 | 2026-06-15 | Outstanding: 600.00"`.
   First item is auto-selected. Changing selection updates the Amount Received range and Remaining label.
2. **Selected Invoice Outstanding Balance**: read-only label showing the current outstanding of the selected invoice.
3. **Amount Received**: QDoubleSpinBox (range: 0.01 to selected invoice's outstanding balance).
4. **Remaining After Payment**: read-only label, updates live as amount changes.
5. **Notes**: optional QLineEdit.
6. Buttons: "Confirm Payment" (primary) | Cancel.

### Behaviour
- When the invoice selector changes: update the outstanding label, reset amount_spin range and value, recalculate remaining.
- On Confirm: calls `customers_logic.record_payment(customer_id, selected_sale_id, amount, notes)`.
- On success: shows QMessageBox confirmation, calls `self.accept()`.
- On `ValueError` or DB error: shows QMessageBox, dialog stays open.
- If no outstanding invoices exist when dialog opens: show an informational message and close immediately (edge case: balance became zero between button click and dialog open).

---

## sales_page.py Changes

### Customer Selector
- Replace `self.customer_input` QLineEdit with `self.customer_combo` (editable QComboBox).
- Populated from `customers_logic.get_all_customers_for_selector()`.
- First item: "(Select or add customer)" with `userData=None`.
- Last item: "＋ Add New Customer…" triggers `AddCustomerDialog` (name + optional phone).
- Selected `customer_id` stored in `self._selected_customer_id`.
- Invoice MUST NOT save when `self._selected_customer_id is None`.

### Payment Status Selector (replaces "Paid in Full" checkbox)
Replace the single "Paid in Full" checkbox with a `QComboBox` named `self.payment_status_combo` containing:
- `"Paid in Full"` (index 0, default)
- `"Partial Payment"` (index 1)
- `"Unpaid"` (index 2)

When the selection changes:
- **"Paid in Full"**: hide partial-payment fields; `amount_paid = invoice_total`.
- **"Partial Payment"**: show `amount_paid` QDoubleSpinBox and Remaining Balance label.
- **"Unpaid"**: hide partial-payment fields; `amount_paid = 0`.

### Partial Payment Fields (shown only for "Partial Payment")
- Invoice Total label (read-only, mirrors footer total)
- `self.amount_paid_spin` — QDoubleSpinBox (range 0 to invoice_total)
- Remaining Balance label (auto-updated live)

### On Save
1. Validate customer selected.
2. Compute `amount_paid` based on payment_status_combo selection.
3. Call `customers_logic.validate_partial_payment(invoice_total, amount_paid)` inside try/except.
4. Pass `customer_id`, `amount_paid` to `sales_db.insert_sale_with_items`.
5. Reset combo to "Paid in Full" and refresh customer combo on success.

---

## dashboard_page.py Changes

Two new KPI cards added to the existing grid:

### Outstanding Receivables Card (clickable)
- Value: `customers_logic.get_outstanding_receivables_total()`
- Clicking opens `ReceivablesListDialog` (inline dialog listing customers with balance)
- Dialog: QTableWidget with Customer Name | Outstanding Balance; double-click navigates to customer profile
- Emits `navigate_to_customer(customer_id: int)` Signal

### Customers With Balance Card (display only)
- Value: `customers_logic.get_customers_with_outstanding_count()`

Both cards refreshed in the existing KPI refresh method.

---

## reports_page.py Changes

New "Customer Receivables" tab added to existing QTabWidget:
- Search bar (name filter)
- Date-range filter (reuse existing date filter widget style)
- QTableWidget: Customer | Total Sales | Total Paid | Outstanding Balance
- Sortable columns
- Data from `customers_logic.get_receivables_report(start_date, end_date, search)`
- Refreshed when tab is selected or date filter applied
