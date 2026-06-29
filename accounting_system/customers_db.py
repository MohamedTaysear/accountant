import database


def create_customer(name: str, phone: str) -> int:
    conn = database.get_connection()
    try:
        conn.execute(
            "INSERT INTO Customers (name, phone, created_at) VALUES (?, ?, ?)",
            (name, phone, database.now_cairo())
        )
        row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        return row_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_all_customers() -> list:
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT id, name, phone FROM Customers ORDER BY name COLLATE NOCASE ASC"
        ).fetchall()
    finally:
        conn.close()


def get_customer_by_id(customer_id: int):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT id, name, phone FROM Customers WHERE id = ?", (customer_id,)
        ).fetchone()
    finally:
        conn.close()


def get_customers_with_balance_summary() -> list:
    conn = database.get_connection()
    try:
        return conn.execute("""
            SELECT
                c.id,
                c.name,
                c.phone,
                COUNT(s.id)                                       AS invoice_count,
                COALESCE(SUM(s.total_amount), 0)                  AS total_purchases,
                COALESCE(SUM(s.amount_paid), 0)                   AS total_paid_at_invoice,
                COALESCE((
                    SELECT SUM(p.amount)
                    FROM Payments p
                    WHERE p.customer_id = c.id
                ), 0)                                             AS total_post_payments,
                COALESCE(SUM(s.total_amount - s.amount_paid), 0) -
                COALESCE((
                    SELECT SUM(p.amount)
                    FROM Payments p
                    WHERE p.customer_id = c.id
                ), 0)                                             AS outstanding_balance
            FROM Customers c
            LEFT JOIN Sales s ON s.customer_id = c.id AND s.status = 'active'
            GROUP BY c.id
            ORDER BY c.name COLLATE NOCASE ASC
        """).fetchall()
    finally:
        conn.close()


def get_customer_invoices(customer_id: int) -> list:
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT id, invoice_number, created_at, total_amount, amount_paid, status
               FROM Sales
               WHERE customer_id = ?
               ORDER BY created_at ASC""",
            (customer_id,)
        ).fetchall()
    finally:
        conn.close()


def get_invoice_outstanding(sale_id: int) -> float:
    conn = database.get_connection()
    try:
        inv = conn.execute(
            "SELECT total_amount, amount_paid, status FROM Sales WHERE id = ?", (sale_id,)
        ).fetchone()
        if not inv or inv["status"] == "voided":
            return 0.0
        paid = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM Payments WHERE sale_id = ?", (sale_id,)
        ).fetchone()[0]
        return max(0.0, round(float(inv["total_amount"]) - float(inv["amount_paid"]) - float(paid), 2))
    finally:
        conn.close()


def get_outstanding_receivables_total() -> float:
    conn = database.get_connection()
    try:
        inv_remaining = conn.execute(
            "SELECT COALESCE(SUM(total_amount - amount_paid), 0) FROM Sales WHERE status = 'active' AND customer_id IS NOT NULL"
        ).fetchone()[0]
        pay_total = conn.execute(
            "SELECT COALESCE(SUM(p.amount), 0) FROM Payments p JOIN Sales s ON p.sale_id = s.id WHERE s.status = 'active'"
        ).fetchone()[0]
        return max(0.0, round(float(inv_remaining) - float(pay_total), 2))
    finally:
        conn.close()


def get_customers_with_outstanding_balance() -> list:
    rows = get_customers_with_balance_summary()
    return [r for r in rows if float(r["outstanding_balance"]) > 0]
