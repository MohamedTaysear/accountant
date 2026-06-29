# Contract: logic/customers_logic.py

**Layer**: Business Logic | **Feature**: 008-customer-credit-receivables

MUST NOT import PySide6. MUST NOT contain raw SQL. Imports `customers_db`, `payments_db`, `database`.

---

## Customer Management

### `validate_customer_name(name: str) -> str`
Strips whitespace. Raises `ValueError("Customer name cannot be empty.")` if blank. Returns stripped name.

### `create_customer(name: str, phone: str) -> int`
Validates name. Calls `customers_db.create_customer`. Returns new customer id.

### `get_all_customers_for_selector() -> list[dict]`
Returns `[{"id": int, "name": str, "phone": str}, ...]` for the sales-page combo box.

### `get_customers_list() -> list[dict]`
Returns full summary list from `customers_db.get_customers_with_balance_summary()` as list of dicts.

---

## Partial-Payment Validation (used by sales_logic)

### `validate_partial_payment(invoice_total: float, amount_paid: float) -> None`
- Raises `ValueError("Amount paid cannot be negative.")` if `amount_paid < 0`.
- Raises `ValueError("Amount paid cannot exceed the invoice total.")` if `amount_paid > invoice_total`.

### `compute_invoice_outstanding(sale_id: int) -> float`
Delegates to `customers_db.get_invoice_outstanding(sale_id)`.
Returns the current outstanding balance for a specific invoice.

---

## Payment Collection

### `validate_payment_amount(amount: float, invoice_outstanding: float) -> None`
- Raises `ValueError("Payment amount must be greater than zero.")` if `amount <= 0`.
- Raises `ValueError("Payment cannot exceed the invoice outstanding balance.")` if `amount > invoice_outstanding + 0.001`.

### `record_payment(customer_id: int, sale_id: int, amount: float, notes: str = "") -> int`
1. Fetches current `invoice_outstanding = compute_invoice_outstanding(sale_id)`.
2. Calls `validate_payment_amount(amount, invoice_outstanding)`.
3. Computes `remaining_after = round(invoice_outstanding - amount, 2)`.
4. Opens a `database.get_connection()` transaction.
5. Calls `payments_db.insert_payment(customer_id, sale_id, amount, remaining_after, notes, conn)`.
6. Commits. Returns new payment id.
7. On any exception: rollback, re-raise.

---

## Customer Profile

### `get_customer_profile(customer_id: int) -> dict`
Returns:
```python
{
    "customer": dict,                  # name, phone
    "outstanding_balance": float,      # sum of per-invoice outstanding (active only)
    "total_purchases": float,
    "total_paid": float,               # amount_paid + all post-sale payments
    "invoice_count": int,
    "invoices": list[dict],            # per-invoice with derived paid/remaining/status
    "payments": list[dict],            # raw payment records for payment history tab
}
```

Per-invoice dict structure:
```python
{
    "id": int,
    "invoice_number": str,
    "created_at": str,
    "total_amount": float,
    "amount_paid_at_creation": float,  # what was paid when invoice was saved
    "post_sale_payments": float,       # SUM of payments.amount for this invoice
    "total_paid": float,               # amount_paid_at_creation + post_sale_payments
    "remaining": float,                # total_amount - total_paid
    "payment_status": str,             # "Paid" / "Partially Paid" / "Unpaid" / "Voided"
}
```

No FIFO. Each invoice's values computed independently from `payments_db.get_total_payments_for_invoice(sale_id)`.

### `get_outstanding_invoices_for_customer(customer_id: int) -> list[dict]`
Returns only the invoices with `remaining > 0` and `status = 'active'`.
Used to populate the "select invoice" list in the Receive Payment dialog.
Each dict includes: `id, invoice_number, created_at, total_amount, remaining`.

---

## Dashboard / Report Aggregates

### `get_outstanding_receivables_total() -> float`
Delegates to `customers_db.get_outstanding_receivables_total()`.

### `get_customers_with_outstanding_count() -> int`
Returns count of customers where outstanding_balance > 0.

### `get_customers_with_outstanding_list() -> list[dict]`
Returns `[{"id": int, "name": str, "outstanding_balance": float}, ...]`.

### `get_receivables_report(start_date=None, end_date=None, search=None) -> list[dict]`
Returns per-customer receivables summary. Date filter scopes invoices by `created_at`. Search filters by customer name.
Columns per dict: `name, total_sales, total_paid, outstanding_balance`.
