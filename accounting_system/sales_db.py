import database


def get_next_invoice_number() -> str:
    conn = database.get_connection()
    try:
        row = conn.execute("SELECT MAX(id) FROM Sales").fetchone()
        max_id = row[0] if row[0] is not None else 0
        return f"SAL-{max_id + 1:06d}"
    finally:
        conn.close()


def insert_sale_with_items(customer_name, discount_amount: float, items: list,
                           customer_id=None, amount_paid=None) -> str:
    subtotal = sum(item["subtotal"] for item in items)
    total_amount = subtotal - discount_amount
    ap = amount_paid if amount_paid is not None else total_amount
    conn = database.get_connection()
    try:
        conn.execute(
            "INSERT INTO Sales (invoice_number, customer_name, discount_amount, total_amount,"
            " status, created_at, customer_id, amount_paid)"
            " VALUES (?, ?, ?, ?, 'active', ?, ?, ?)",
            ("PENDING", customer_name, discount_amount, total_amount,
             database.now_cairo(), customer_id, ap)
        )
        sale_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        invoice_number = f"SAL-{sale_id:06d}"
        conn.execute(
            "UPDATE Sales SET invoice_number = ? WHERE id = ?",
            (invoice_number, sale_id)
        )
        for item in items:
            purchase_price_at_sale = conn.execute(
                "SELECT purchase_price FROM Products WHERE id = ?",
                (item["product_id"],)
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO SaleItems (sale_id, product_id, quantity, unit_price, purchase_price_at_sale, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                (sale_id, item["product_id"], item["quantity"], item["unit_price"], purchase_price_at_sale, item["subtotal"])
            )
            conn.execute(
                "UPDATE Products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (item["quantity"], item["product_id"])
            )
        conn.commit()
        return invoice_number
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_sale_by_id(sale_id: int):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT * FROM Sales WHERE id = ?", (sale_id,)
        ).fetchone()
    finally:
        conn.close()


def get_sale_items(sale_id: int):
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT si.*, p.name as product_name
               FROM SaleItems si
               JOIN Products p ON si.product_id = p.id
               WHERE si.sale_id = ?""",
            (sale_id,)
        ).fetchall()
    finally:
        conn.close()


def get_all_sales(start_date=None, end_date=None, search=None):
    conn = database.get_connection()
    try:
        conditions = []
        params = []
        if start_date and end_date:
            conditions.append("DATE(created_at) BETWEEN ? AND ?")
            params.extend([start_date, end_date])
        if search:
            conditions.append(
                "(invoice_number LIKE ? COLLATE NOCASE"
                " OR customer_name LIKE ? COLLATE NOCASE"
                " OR status LIKE ? COLLATE NOCASE)"
            )
            like = f"%{search}%"
            params.extend([like, like, like])
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return conn.execute(
            f"SELECT * FROM Sales {where} ORDER BY created_at DESC",
            params
        ).fetchall()
    finally:
        conn.close()


def get_total_sales_amount(start_date=None, end_date=None) -> float:
    conn = database.get_connection()
    try:
        if start_date and end_date:
            row = conn.execute(
                """SELECT COALESCE(SUM(total_amount), 0.0) AS val FROM Sales
                   WHERE status='active' AND DATE(created_at) BETWEEN ? AND ?""",
                (start_date, end_date)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COALESCE(SUM(total_amount), 0.0) AS val FROM Sales WHERE status='active'"
            ).fetchone()
        return float(row["val"])
    finally:
        conn.close()


def get_profit_components(start_date=None, end_date=None) -> dict:
    conn = database.get_connection()
    try:
        if start_date and end_date:
            row = conn.execute(
                """SELECT COALESCE(SUM(si.subtotal), 0.0)                        AS revenue,
                          COALESCE(SUM(si.quantity * si.purchase_price_at_sale), 0.0) AS cost,
                          COALESCE(SUM(s.discount_amount), 0.0)                  AS discount
                   FROM SaleItems si
                   JOIN Sales s ON si.sale_id = s.id
                   WHERE s.status='active' AND DATE(s.created_at) BETWEEN ? AND ?""",
                (start_date, end_date)
            ).fetchone()
        else:
            row = conn.execute(
                """SELECT COALESCE(SUM(si.subtotal), 0.0)                        AS revenue,
                          COALESCE(SUM(si.quantity * si.purchase_price_at_sale), 0.0) AS cost,
                          COALESCE(SUM(s.discount_amount), 0.0)                  AS discount
                   FROM SaleItems si
                   JOIN Sales s ON si.sale_id = s.id
                   WHERE s.status='active'"""
            ).fetchone()
        return {
            "revenue":  float(row["revenue"]),
            "cost":     float(row["cost"]),
            "discount": float(row["discount"]),
        }
    finally:
        conn.close()


def get_recent_activity(limit: int = 10) -> list:
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT invoice_number,
                      'Sale'         AS type,
                      customer_name  AS party,
                      total_amount,
                      created_at
               FROM Sales
               UNION ALL
               SELECT invoice_number,
                      'Purchase'     AS type,
                      supplier_name  AS party,
                      total_amount,
                      created_at
               FROM Purchases
               UNION ALL
               SELECT invoice_number   AS invoice_number,
                      'Expense'        AS type,
                      ''               AS party,
                      total_amount     AS total_amount,
                      expense_datetime AS created_at
               FROM ExpenseInvoices
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
    finally:
        conn.close()


def get_top_selling_products(start_date=None, end_date=None) -> list:
    conn = database.get_connection()
    try:
        if start_date and end_date:
            return conn.execute(
                """SELECT p.name AS product_name, SUM(si.quantity) AS total_quantity
                   FROM SaleItems si
                   JOIN Sales s ON si.sale_id = s.id
                   JOIN Products p ON si.product_id = p.id
                   WHERE s.status='active' AND DATE(s.created_at) BETWEEN ? AND ?
                   GROUP BY si.product_id
                   ORDER BY total_quantity DESC""",
                (start_date, end_date)
            ).fetchall()
        else:
            return conn.execute(
                """SELECT p.name AS product_name, SUM(si.quantity) AS total_quantity
                   FROM SaleItems si
                   JOIN Sales s ON si.sale_id = s.id
                   JOIN Products p ON si.product_id = p.id
                   WHERE s.status='active'
                   GROUP BY si.product_id
                   ORDER BY total_quantity DESC"""
            ).fetchall()
    finally:
        conn.close()


def void_sale(sale_id: int) -> None:
    conn = database.get_connection()
    try:
        items = conn.execute(
            "SELECT product_id, quantity FROM SaleItems WHERE sale_id = ?",
            (sale_id,)
        ).fetchall()
        conn.execute(
            "UPDATE Sales SET status = 'voided' WHERE id = ?",
            (sale_id,)
        )
        for item in items:
            conn.execute(
                "UPDATE Products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (item["quantity"], item["product_id"])
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
