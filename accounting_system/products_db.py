import sqlite3
import database


def insert_product(name: str, category: str, purchase_price: float,
                   selling_price: float, stock_quantity: float,
                   reorder_level: float) -> None:
    conn = database.get_connection()
    try:
        conn.execute(
            """INSERT INTO Products
               (name, category, purchase_price, selling_price,
                stock_quantity, reorder_level)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, category, purchase_price, selling_price,
             stock_quantity, reorder_level)
        )
        conn.commit()
    finally:
        conn.close()


def update_product(product_id: int, name: str, category: str,
                   purchase_price: float, selling_price: float,
                   stock_quantity: float, reorder_level: float) -> None:
    conn = database.get_connection()
    try:
        conn.execute(
            """UPDATE Products SET name=?, category=?, purchase_price=?,
               selling_price=?, stock_quantity=?, reorder_level=?
               WHERE id=?""",
            (name, category, purchase_price, selling_price,
             stock_quantity, reorder_level, product_id)
        )
        conn.commit()
    finally:
        conn.close()


def delete_product(product_id: int) -> None:
    conn = database.get_connection()
    try:
        conn.execute("DELETE FROM Products WHERE id = ?", (product_id,))
        conn.commit()
    finally:
        conn.close()


def set_active(product_id: int, is_active: int) -> None:
    conn = database.get_connection()
    try:
        conn.execute(
            "UPDATE Products SET is_active = ? WHERE id = ?",
            (is_active, product_id)
        )
        conn.commit()
    finally:
        conn.close()


def search_products(search_text: str, include_inactive: bool):
    conn = database.get_connection()
    try:
        pattern = f"%{search_text}%"
        if include_inactive:
            return conn.execute(
                "SELECT * FROM Products WHERE name LIKE ? ORDER BY name",
                (pattern,)
            ).fetchall()
        else:
            return conn.execute(
                """SELECT * FROM Products
                   WHERE name LIKE ? AND is_active = 1
                   ORDER BY name""",
                (pattern,)
            ).fetchall()
    finally:
        conn.close()


def get_active_products():
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT id, name, selling_price, stock_quantity
               FROM Products WHERE is_active = 1 ORDER BY name"""
        ).fetchall()
    finally:
        conn.close()


def get_low_stock_products():
    conn = database.get_connection()
    try:
        return conn.execute(
            """SELECT id, name, category, stock_quantity, reorder_level
               FROM Products
               WHERE is_active = 1 AND stock_quantity <= reorder_level
               ORDER BY name"""
        ).fetchall()
    finally:
        conn.close()


def get_categories():
    """Return distinct non-empty category values, sorted alphabetically."""
    conn = database.get_connection()
    try:
        rows = conn.execute(
            """SELECT DISTINCT category FROM Products
               WHERE category != '' ORDER BY category"""
        ).fetchall()
        return [row["category"] for row in rows]
    finally:
        conn.close()


def is_product_referenced(product_id: int) -> bool:
    conn = database.get_connection()
    try:
        row = conn.execute(
            """SELECT 1 FROM SaleItems WHERE product_id = ?
               UNION
               SELECT 1 FROM PurchaseItems WHERE product_id = ?
               LIMIT 1""",
            (product_id, product_id)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def get_product_by_id(product_id: int):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT * FROM Products WHERE id = ?", (product_id,)
        ).fetchone()
    finally:
        conn.close()


def get_product_counts() -> dict:
    conn = database.get_connection()
    try:
        row = conn.execute(
            """SELECT COUNT(*) AS total,
                      SUM(CASE WHEN is_active=1 THEN 1 ELSE 0 END) AS active,
                      SUM(CASE WHEN is_active=0 THEN 1 ELSE 0 END) AS inactive
               FROM Products"""
        ).fetchone()
        return {
            "total":    row["total"]    or 0,
            "active":   row["active"]   or 0,
            "inactive": row["inactive"] or 0,
        }
    finally:
        conn.close()


def get_inventory_value() -> float:
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(stock_quantity * purchase_price), 0.0) AS val FROM Products"
        ).fetchone()
        return float(row["val"])
    finally:
        conn.close()


def get_potential_stock_profit() -> float:
    conn = database.get_connection()
    try:
        row = conn.execute(
            """SELECT COALESCE(SUM((selling_price - purchase_price) * stock_quantity), 0.0) AS val
               FROM Products"""
        ).fetchone()
        return float(row["val"])
    finally:
        conn.close()


def get_potential_sales_value() -> float:
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(selling_price * stock_quantity), 0.0) AS val FROM Products"
        ).fetchone()
        return float(row["val"])
    finally:
        conn.close()


def get_low_stock_count() -> int:
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM Products WHERE is_active=1 AND stock_quantity <= reorder_level"
        ).fetchone()
        return int(row["cnt"])
    finally:
        conn.close()
