import database


def insert_payment(customer_id: int, sale_id: int, amount: float,
                   remaining_after: float, notes: str, conn) -> int:
    """Insert a payment using the provided connection (caller manages transaction)."""
    conn.execute(
        """INSERT INTO Payments
           (customer_id, sale_id, amount, remaining_after, notes, payment_date, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (customer_id, sale_id, amount, remaining_after, notes,
         database.now_cairo(), database.now_cairo())
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_payments_for_customer(customer_id: int) -> list:
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT p.id, p.customer_id, p.sale_id, p.amount, p.notes,
                      p.remaining_after, p.payment_date, p.created_at,
                      s.invoice_number
               FROM Payments p
               JOIN Sales s ON p.sale_id = s.id
               WHERE p.customer_id = ?
               ORDER BY p.payment_date ASC""",
            (customer_id,)
        ).fetchall()
    finally:
        conn.close()


def get_payments_for_invoice(sale_id: int) -> list:
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT id, customer_id, sale_id, amount, notes, remaining_after,
                      payment_date, created_at
               FROM Payments WHERE sale_id = ? ORDER BY payment_date ASC""",
            (sale_id,)
        ).fetchall()
    finally:
        conn.close()


def get_total_payments_for_invoice(sale_id: int) -> float:
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM Payments WHERE sale_id = ?", (sale_id,)
        ).fetchone()
        return float(row[0])
    finally:
        conn.close()


def get_total_payments_for_customer(customer_id: int) -> float:
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM Payments WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        return float(row[0])
    finally:
        conn.close()
