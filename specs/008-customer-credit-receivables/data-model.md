# Data Model: Customer Credit & Receivables Management

**Feature**: 008-customer-credit-receivables | **Date**: 2026-06-29 (revised 2026-06-29)

## New Tables

### Customers

```sql
CREATE TABLE IF NOT EXISTS Customers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    phone      TEXT    NOT NULL DEFAULT '',
    created_at TEXT    NOT NULL
);
```

| Column | Type | Rules |
|--------|------|-------|
| `id` | INTEGER PK | Auto-assigned |
| `name` | TEXT NOT NULL | Non-empty after strip |
| `phone` | TEXT DEFAULT '' | Optional |
| `created_at` | TEXT NOT NULL | `database.now_cairo()` at insert |

**Relationships**: `Sales.customer_id → Customers.id`

---

### Payments

Each payment is linked to **both** the customer and the specific invoice it settles. This is the canonical architecture — enables per-invoice history, future statements, and aging reports without reconstruction.

```sql
CREATE TABLE IF NOT EXISTS Payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL,
    sale_id         INTEGER NOT NULL,
    amount          REAL    NOT NULL,
    notes           TEXT    NOT NULL DEFAULT '',
    remaining_after REAL    NOT NULL,
    payment_date    TEXT    NOT NULL,
    created_at      TEXT    NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(id),
    FOREIGN KEY (sale_id)     REFERENCES Sales(id)
);
```

| Column | Type | Rules |
|--------|------|-------|
| `id` | INTEGER PK | Auto-assigned |
| `customer_id` | INTEGER NOT NULL FK | Must reference an existing Customer |
| `sale_id` | INTEGER NOT NULL FK | The specific invoice this payment settles (partially or fully) |
| `amount` | REAL NOT NULL | Must be > 0 and ≤ invoice outstanding balance at time of recording |
| `notes` | TEXT DEFAULT '' | Optional |
| `remaining_after` | REAL NOT NULL | Snapshot: remaining balance of the invoice **after** this payment (audit trail) |
| `payment_date` | TEXT NOT NULL | `database.now_cairo()` at insert |
| `created_at` | TEXT NOT NULL | `database.now_cairo()` at insert |

**Immutability**: No UPDATE or DELETE operations are ever performed on this table.

---

## Modified Tables

### Sales (existing — new columns added via ALTER TABLE)

```sql
ALTER TABLE Sales ADD COLUMN customer_id  INTEGER REFERENCES Customers(id);
ALTER TABLE Sales ADD COLUMN amount_paid  REAL NOT NULL DEFAULT 0;
```

| New Column | Type | Rules |
|------------|------|-------|
| `customer_id` | INTEGER nullable FK | NULL for historical invoices; required for all new invoices |
| `amount_paid` | REAL DEFAULT 0 | Initial payment collected at invoice creation time. Equals `total_amount` for "Paid in Full". Never updated after save. |

**`remaining_balance` is NOT stored** — it is always derived (see below). The old design stored it; this revision removes it to prevent divergence.

**`customer_name`** column is retained for backward-compatibility with historical invoices. New invoices populate both `customer_id` (FK) and `customer_name` (text copy).

---

## Derived Computations (never stored)

### Per-Invoice Outstanding Balance

```
invoice_outstanding =
    invoice.total_amount
    − invoice.amount_paid
    − SUM(p.amount WHERE p.sale_id = invoice.id)
```

This is always ≥ 0. Computed in `customers_logic.py`, never in UI code.

### Per-Invoice Payment Status (derived label)

```
if invoice.status == 'voided'         → "Voided"
elif invoice_outstanding == 0          → "Paid"
elif invoice.amount_paid == 0
     AND SUM(payments) == 0            → "Unpaid"
else                                   → "Partially Paid"
```

### Customer Outstanding Balance

```
customer_outstanding =
    SUM(invoice_outstanding)
    FOR active Sales WHERE customer_id = X
```

Equivalently in SQL:
```sql
SELECT
    COALESCE(SUM(s.total_amount - s.amount_paid), 0) -
    COALESCE((SELECT SUM(p.amount) FROM Payments p WHERE p.customer_id = c.id), 0)
AS outstanding
FROM Sales s
WHERE s.customer_id = ? AND s.status = 'active'
```

### Total Outstanding Receivables (Dashboard KPI)

```sql
SELECT
    COALESCE(SUM(s.total_amount - s.amount_paid), 0) -
    COALESCE((SELECT SUM(amount) FROM Payments), 0)
AS total_outstanding
FROM Sales s
WHERE s.status = 'active' AND s.customer_id IS NOT NULL
```

### Per-Invoice Total Paid (for profile display)

```
invoice_total_paid =
    invoice.amount_paid
    + SUM(p.amount WHERE p.sale_id = invoice.id)
```

---

## Entity Relationships

```
Customers (1) ──< Sales    (many)    via Sales.customer_id
Customers (1) ──< Payments (many)    via Payments.customer_id
Sales     (1) ──< Payments (many)    via Payments.sale_id      ← key: payment links to invoice
Sales     (1) ──< SaleItems(many)    via SaleItems.sale_id     [existing]
```

---

## Why `remaining_after` is stored on Payments

While `remaining_after` is derivable (recalculate at read time), storing it as a snapshot provides:
1. **Audit trail integrity**: The balance at the moment of payment is recorded permanently, even if future payments or data corrections would change the derived value.
2. **Customer statements**: Future statement generation can report "balance after this payment" without complex re-aggregation.
3. **Tamper evidence**: A discrepancy between the stored snapshot and the derived value signals a data integrity problem.

This is the only intentional redundancy in the model and is justified by the audit-trail requirement (Constitution §IV).
