import sqlite3
import database


def insert_purchase_with_items(supplier_name, items: list) -> str:
    total_amount = sum(item["subtotal"] for item in items)
    conn = database.get_connection()
    try:
        conn.execute(
            """INSERT INTO Purchases (invoice_number, supplier_name, total_amount, status, created_at)
               VALUES (?, ?, ?, 'active', ?)""",
            ("PENDING", supplier_name, total_amount, database.now_cairo())
        )
        purchase_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        invoice_number = f"PUR-{purchase_id:06d}"
        conn.execute(
            "UPDATE Purchases SET invoice_number = ? WHERE id = ?",
            (invoice_number, purchase_id)
        )

        for item in items:
            conn.execute(
                """INSERT INTO PurchaseItems
                   (purchase_id, product_id, quantity, unit_price, subtotal)
                   VALUES (?, ?, ?, ?, ?)""",
                (purchase_id, item["product_id"], item["quantity"],
                 item["unit_price"], item["subtotal"])
            )
            product = conn.execute(
                "SELECT stock_quantity, purchase_price FROM Products WHERE id = ?",
                (item["product_id"],)
            ).fetchone()
            old_qty = product["stock_quantity"]
            old_price = product["purchase_price"]
            new_qty = item["quantity"]
            new_price = item["unit_price"]
            total_qty = old_qty + new_qty
            if total_qty > 0:
                wac = round((old_qty * old_price + new_qty * new_price) / total_qty, 6)
            else:
                wac = new_price
            conn.execute(
                """UPDATE Products
                   SET stock_quantity = stock_quantity + ?,
                       purchase_price = ?
                   WHERE id = ?""",
                (new_qty, wac, item["product_id"])
            )

        conn.commit()
        return invoice_number
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_purchase_by_id(purchase_id: int):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT * FROM Purchases WHERE id = ?", (purchase_id,)
        ).fetchone()
    finally:
        conn.close()


def get_purchase_items(purchase_id: int):
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT pi.*, p.name AS product_name
               FROM PurchaseItems pi
               JOIN Products p ON pi.product_id = p.id
               WHERE pi.purchase_id = ?""",
            (purchase_id,)
        ).fetchall()
    finally:
        conn.close()


def get_all_purchases(start_date=None, end_date=None, search=None):
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
                " OR supplier_name LIKE ? COLLATE NOCASE"
                " OR status LIKE ? COLLATE NOCASE)"
            )
            like = f"%{search}%"
            params.extend([like, like, like])
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return conn.execute(
            f"SELECT * FROM Purchases {where} ORDER BY created_at DESC",
            params
        ).fetchall()
    finally:
        conn.close()


def get_next_invoice_number() -> str:
    conn = database.get_connection()
    try:
        row = conn.execute("SELECT MAX(id) FROM Purchases").fetchone()
        max_id = row[0] if row[0] is not None else 0
        return f"PUR-{max_id + 1:06d}"
    finally:
        conn.close()


def get_total_purchases_amount(start_date=None, end_date=None) -> float:
    conn = database.get_connection()
    try:
        if start_date and end_date:
            row = conn.execute(
                """SELECT COALESCE(SUM(total_amount), 0.0) AS val FROM Purchases
                   WHERE status='active' AND DATE(created_at) BETWEEN ? AND ?""",
                (start_date, end_date)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COALESCE(SUM(total_amount), 0.0) AS val FROM Purchases WHERE status='active'"
            ).fetchone()
        return float(row["val"])
    finally:
        conn.close()


def get_top_purchased_products(start_date=None, end_date=None) -> list:
    conn = database.get_connection()
    try:
        if start_date and end_date:
            return conn.execute(
                """SELECT p.name AS product_name, SUM(pi.quantity) AS total_quantity
                   FROM PurchaseItems pi
                   JOIN Purchases pu ON pi.purchase_id = pu.id
                   JOIN Products p ON pi.product_id = p.id
                   WHERE pu.status='active' AND DATE(pu.created_at) BETWEEN ? AND ?
                   GROUP BY pi.product_id
                   ORDER BY total_quantity DESC""",
                (start_date, end_date)
            ).fetchall()
        else:
            return conn.execute(
                """SELECT p.name AS product_name, SUM(pi.quantity) AS total_quantity
                   FROM PurchaseItems pi
                   JOIN Purchases pu ON pi.purchase_id = pu.id
                   JOIN Products p ON pi.product_id = p.id
                   WHERE pu.status='active'
                   GROUP BY pi.product_id
                   ORDER BY total_quantity DESC"""
            ).fetchall()
    finally:
        conn.close()


def void_purchase(purchase_id: int) -> None:
    conn = database.get_connection()
    try:
        items = conn.execute(
            "SELECT product_id, quantity, unit_price FROM PurchaseItems WHERE purchase_id = ?",
            (purchase_id,)
        ).fetchall()

        for item in items:
            product = conn.execute(
                "SELECT stock_quantity, purchase_price FROM Products WHERE id = ?",
                (item["product_id"],)
            ).fetchone()
            old_qty = product["stock_quantity"]
            old_wac = product["purchase_price"]
            voided_qty = item["quantity"]
            remaining_qty = old_qty - voided_qty
            if remaining_qty > 0:
                reversed_wac = round(
                    (old_qty * old_wac - voided_qty * item["unit_price"]) / remaining_qty, 6
                )
            else:
                reversed_wac = 0.0
            conn.execute(
                """UPDATE Products
                   SET stock_quantity = stock_quantity - ?,
                       purchase_price = ?
                   WHERE id = ?""",
                (voided_qty, reversed_wac, item["product_id"])
            )

        conn.execute(
            "UPDATE Purchases SET status = 'voided' WHERE id = ?",
            (purchase_id,)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
