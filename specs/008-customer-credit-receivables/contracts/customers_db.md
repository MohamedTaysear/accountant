# Contract: customers_db.py & payments_db.py

**Layer**: Data Access | **Feature**: 008-customer-credit-receivables

These modules contain only parameterized SQL. MUST NOT contain business rules. MUST NOT be imported by UI files directly.

---

## customers_db.py

### `create_customer(name: str, phone: str) -> int`
Inserts a new Customer row. Returns new `id`. Sets `created_at = database.now_cairo()`.

### `get_all_customers() -> list[sqlite3.Row]`
Returns all Customers ordered by `name COLLATE NOCASE ASC`.

### `get_customer_by_id(customer_id: int) -> sqlite3.Row | None`
Returns a single Customer row or None.

### `get_customers_with_balance_summary() -> list[sqlite3.Row]`
Returns one row per customer with computed columns:
- `id`, `name`, `phone`
- `invoice_count` — COUNT of active Sales for this customer
- `total_purchases` — SUM of `total_amount` for active Sales
- `total_paid_at_invoice` — SUM of `amount_paid` for active Sales
- `total_post_payments` — SUM of `Payments.amount` for this customer
- `outstanding_balance` = `total_purchases − total_paid_at_invoice − total_post_payments`

Uses LEFT JOINs and correlated subquery; voided invoices excluded via `status = 'active'`.

### `get_customer_invoices(customer_id: int) -> list[sqlite3.Row]`
Returns all Sales rows for the customer ordered by `created_at ASC`.
Columns: `id, invoice_number, created_at, total_amount, amount_paid, status`.
(`remaining_balance` is NOT a column — it is computed in the logic layer.)

### `get_invoice_outstanding(sale_id: int) -> float`
Returns `total_amount − amount_paid − SUM(payments.amount WHERE sale_id = ?)` for one invoice.
Returns 0.0 if the invoice is voided.

### `get_outstanding_receivables_total() -> float`
Scalar: total outstanding across all customers with active invoices.

### `get_customers_with_outstanding_balance() -> list[sqlite3.Row]`
Returns customers where outstanding_balance > 0. Columns: `id, name, outstanding_balance`.

---

## payments_db.py

### `insert_payment(customer_id: int, sale_id: int, amount: float, remaining_after: float, notes: str, conn) -> int`
Inserts a Payment row using the **provided connection** (caller manages transaction).
Sets `payment_date = created_at = database.now_cairo()`. Returns new `id`.

**Signature change from original design**: now accepts `sale_id` and `remaining_after`.

### `get_payments_for_customer(customer_id: int) -> list[sqlite3.Row]`
Returns all Payment rows for the customer ordered by `payment_date ASC`.
Columns: `id, customer_id, sale_id, amount, notes, remaining_after, payment_date, created_at`.

### `get_payments_for_invoice(sale_id: int) -> list[sqlite3.Row]`
Returns all Payment rows for a specific invoice, ordered by `payment_date ASC`.

### `get_total_payments_for_invoice(sale_id: int) -> float`
Scalar: SUM of payment amounts for a specific invoice.

### `get_total_payments_for_customer(customer_id: int) -> float`
Scalar: SUM of all payment amounts for a customer (across all invoices).
