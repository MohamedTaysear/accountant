import database
import customers_db
import payments_db


# ── Customer management ────────────────────────────────────────────────────

def validate_customer_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("Customer name cannot be empty.")
    return name


def create_customer(name: str, phone: str) -> int:
    name = validate_customer_name(name)
    return customers_db.create_customer(name, (phone or "").strip())


def get_all_customers_for_selector() -> list:
    rows = customers_db.get_all_customers()
    return [{"id": r["id"], "name": r["name"], "phone": r["phone"]} for r in rows]


def get_customers_list() -> list:
    return [dict(r) for r in customers_db.get_customers_with_balance_summary()]


# ── Partial-payment validation ────────────────────────────────────────────

def validate_partial_payment(invoice_total: float, amount_paid: float) -> None:
    if amount_paid < 0:
        raise ValueError("Amount paid cannot be negative.")
    if amount_paid > invoice_total + 0.001:
        raise ValueError("Amount paid cannot exceed the invoice total.")


def compute_invoice_outstanding(sale_id: int) -> float:
    return customers_db.get_invoice_outstanding(sale_id)


# ── Payment collection ────────────────────────────────────────────────────

def validate_payment_amount(amount: float, invoice_outstanding: float) -> None:
    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")
    if amount > invoice_outstanding + 0.001:
        raise ValueError("Payment cannot exceed the invoice outstanding balance.")


def record_payment(customer_id: int, sale_id: int, amount: float, notes: str = "") -> int:
    invoice_outstanding = compute_invoice_outstanding(sale_id)
    validate_payment_amount(amount, invoice_outstanding)
    remaining_after = round(invoice_outstanding - amount, 2)
    conn = database.get_connection()
    try:
        payment_id = payments_db.insert_payment(
            customer_id, sale_id, amount, remaining_after, notes, conn
        )
        conn.commit()
        return payment_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Customer profile ──────────────────────────────────────────────────────

def _derive_payment_status(total_amount: float, total_paid: float, inv_status: str) -> str:
    if inv_status == "voided":
        return "Voided"
    remaining = round(total_amount - total_paid, 2)
    if remaining <= 0:
        return "Paid"
    if total_paid <= 0:
        return "Unpaid"
    return "Partially Paid"


def get_customer_profile(customer_id: int) -> dict:
    customer = customers_db.get_customer_by_id(customer_id)
    if not customer:
        raise ValueError(f"Customer {customer_id} not found.")

    invoices_raw = customers_db.get_customer_invoices(customer_id)
    all_payments = payments_db.get_payments_for_customer(customer_id)

    total_purchases = 0.0
    total_paid_sum  = 0.0
    outstanding_sum = 0.0
    invoices = []

    for inv in invoices_raw:
        inv_total      = float(inv["total_amount"])
        paid_at_create = float(inv["amount_paid"])
        post_payments  = payments_db.get_total_payments_for_invoice(inv["id"])
        total_paid_inv = round(paid_at_create + post_payments, 2)
        remaining      = max(0.0, round(inv_total - total_paid_inv, 2))
        status         = _derive_payment_status(inv_total, total_paid_inv, inv["status"])

        total_purchases += inv_total
        total_paid_sum  += total_paid_inv
        if inv["status"] == "active":
            outstanding_sum += remaining

        invoices.append({
            "id": inv["id"],
            "invoice_number": inv["invoice_number"],
            "created_at": inv["created_at"],
            "total_amount": inv_total,
            "amount_paid_at_creation": paid_at_create,
            "post_sale_payments": post_payments,
            "total_paid": total_paid_inv,
            "remaining": remaining,
            "payment_status": status,
        })

    return {
        "customer": dict(customer),
        "outstanding_balance": round(outstanding_sum, 2),
        "total_purchases": round(total_purchases, 2),
        "total_paid": round(total_paid_sum, 2),
        "invoice_count": len(invoices_raw),
        "invoices": invoices,
        "payments": [dict(p) for p in all_payments],
    }


def get_outstanding_invoices_for_customer(customer_id: int) -> list:
    """Returns only invoices with remaining > 0, for the Receive Payment dialog."""
    invoices_raw = customers_db.get_customer_invoices(customer_id)
    result = []
    for inv in invoices_raw:
        if inv["status"] != "active":
            continue
        outstanding = customers_db.get_invoice_outstanding(inv["id"])
        if outstanding > 0:
            result.append({
                "id": inv["id"],
                "invoice_number": inv["invoice_number"],
                "created_at": inv["created_at"],
                "total_amount": float(inv["total_amount"]),
                "remaining": outstanding,
            })
    return result


# ── Dashboard / report aggregates ────────────────────────────────────────

def get_outstanding_receivables_total() -> float:
    return customers_db.get_outstanding_receivables_total()


def get_customers_with_outstanding_count() -> int:
    return len(customers_db.get_customers_with_outstanding_balance())


def get_customers_with_outstanding_list() -> list:
    rows = customers_db.get_customers_with_outstanding_balance()
    return [{"id": r["id"], "name": r["name"],
             "outstanding_balance": float(r["outstanding_balance"])} for r in rows]


def get_receivables_report(start_date=None, end_date=None, search=None) -> list:
    conn = database.get_connection()
    try:
        conditions = ["s.status = 'active'"]
        params = []
        if start_date and end_date:
            conditions.append("DATE(s.created_at) BETWEEN ? AND ?")
            params.extend([start_date, end_date])
        where = " AND ".join(conditions)
        rows = conn.execute(f"""
            SELECT
                c.id,
                c.name,
                COALESCE(SUM(s.total_amount), 0)             AS total_sales,
                COALESCE(SUM(s.amount_paid), 0)              AS paid_at_invoice,
                COALESCE(SUM(s.total_amount - s.amount_paid), 0) AS inv_remaining
            FROM Customers c
            LEFT JOIN Sales s ON s.customer_id = c.id AND {where}
            GROUP BY c.id
            ORDER BY c.name COLLATE NOCASE ASC
        """, params).fetchall()
    finally:
        conn.close()

    results = []
    for r in rows:
        if search and search.lower() not in r["name"].lower():
            continue
        post = payments_db.get_total_payments_for_customer(r["id"])
        outstanding = max(0.0, round(float(r["inv_remaining"]) - post, 2))
        total_paid  = round(float(r["paid_at_invoice"]) + post, 2)
        results.append({
            "name": r["name"],
            "total_sales": round(float(r["total_sales"]), 2),
            "total_paid": total_paid,
            "outstanding_balance": outstanding,
        })
    return results
