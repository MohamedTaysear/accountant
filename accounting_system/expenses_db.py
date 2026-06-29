import database


# ---------------------------------------------------------------------------
# ExpenseInvoices + ExpenseItems  (current invoice-based model)
# ---------------------------------------------------------------------------

def get_next_invoice_number() -> str:
    conn = database.get_connection()
    try:
        row = conn.execute("SELECT MAX(id) FROM ExpenseInvoices").fetchone()
        max_id = row[0] if row[0] is not None else 0
        return f"EXP-{max_id + 1:06d}"
    finally:
        conn.close()


def insert_expense_invoice(expense_datetime: str, items: list) -> str:
    """Insert an invoice + its line items in a single transaction.

    items: list of {category, description, amount, notes}
    Returns the generated invoice_number.
    """
    total_amount = sum(item["amount"] for item in items)
    conn = database.get_connection()
    try:
        conn.execute(
            """INSERT INTO ExpenseInvoices
               (invoice_number, expense_datetime, total_amount, created_at)
               VALUES ('PENDING', ?, ?, ?)""",
            (expense_datetime, total_amount, database.now_cairo()),
        )
        invoice_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        invoice_number = f"EXP-{invoice_id:06d}"
        conn.execute(
            "UPDATE ExpenseInvoices SET invoice_number = ? WHERE id = ?",
            (invoice_number, invoice_id),
        )
        for item in items:
            conn.execute(
                """INSERT INTO ExpenseItems
                   (invoice_id, category, description, amount, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    invoice_id,
                    item["category"],
                    item.get("description", ""),
                    item["amount"],
                    item.get("notes", ""),
                ),
            )
        conn.commit()
        return invoice_number
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_expense_invoice(invoice_id: int) -> None:
    conn = database.get_connection()
    try:
        conn.execute("DELETE FROM ExpenseItems WHERE invoice_id = ?", (invoice_id,))
        conn.execute("DELETE FROM ExpenseInvoices WHERE id = ?", (invoice_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_expense_invoice_by_id(invoice_id: int):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT * FROM ExpenseInvoices WHERE id = ?", (invoice_id,)
        ).fetchone()
    finally:
        conn.close()


def get_expense_items_by_invoice(invoice_id: int) -> list:
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT * FROM ExpenseItems WHERE invoice_id = ? ORDER BY id",
            (invoice_id,),
        ).fetchall()
    finally:
        conn.close()


def get_all_expense_invoices(start_date=None, end_date=None, search=None) -> list:
    conn = database.get_connection()
    try:
        conditions, params = [], []
        if start_date and end_date:
            conditions.append("DATE(expense_datetime) BETWEEN ? AND ?")
            params.extend([start_date, end_date])
        if search:
            conditions.append("invoice_number LIKE ? COLLATE NOCASE")
            params.append(f"%{search}%")
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        return conn.execute(
            f"""SELECT * FROM ExpenseInvoices {where}
                ORDER BY expense_datetime DESC, id DESC""",
            params,
        ).fetchall()
    finally:
        conn.close()


def get_distinct_categories() -> list:
    conn = database.get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT category FROM ExpenseItems ORDER BY category COLLATE NOCASE"
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def get_total_expenses(start_date=None, end_date=None) -> float:
    conn = database.get_connection()
    try:
        if start_date and end_date:
            row = conn.execute(
                """SELECT COALESCE(SUM(total_amount), 0.0) AS val
                   FROM ExpenseInvoices
                   WHERE DATE(expense_datetime) BETWEEN ? AND ?""",
                (start_date, end_date),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COALESCE(SUM(total_amount), 0.0) AS val FROM ExpenseInvoices"
            ).fetchone()
        return float(row["val"])
    finally:
        conn.close()


def get_top_expense_categories(start_date=None, end_date=None) -> list:
    conn = database.get_connection()
    try:
        if start_date and end_date:
            rows = conn.execute(
                """SELECT ei.category, SUM(ei.amount) AS total_amount
                   FROM ExpenseItems ei
                   JOIN ExpenseInvoices inv ON inv.id = ei.invoice_id
                   WHERE DATE(inv.expense_datetime) BETWEEN ? AND ?
                   GROUP BY ei.category COLLATE NOCASE
                   ORDER BY total_amount DESC""",
                (start_date, end_date),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT category, SUM(amount) AS total_amount
                   FROM ExpenseItems
                   GROUP BY category COLLATE NOCASE
                   ORDER BY total_amount DESC"""
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_expenses_for_report(start_date=None, end_date=None,
                            category=None, search=None) -> list:
    """Invoice-level rows for the Reports page.

    category filters invoices that contain at least one item in that category.
    search matches invoice_number or any item field.
    """
    conn = database.get_connection()
    try:
        conditions, params = [], []
        if start_date and end_date:
            conditions.append("DATE(inv.expense_datetime) BETWEEN ? AND ?")
            params.extend([start_date, end_date])
        if category:
            conditions.append(
                "inv.id IN (SELECT invoice_id FROM ExpenseItems"
                " WHERE category = ? COLLATE NOCASE)"
            )
            params.append(category)
        if search:
            like = f"%{search}%"
            conditions.append(
                "(inv.invoice_number LIKE ? COLLATE NOCASE"
                " OR EXISTS (SELECT 1 FROM ExpenseItems ei"
                "  WHERE ei.invoice_id = inv.id"
                "  AND (ei.category    LIKE ? COLLATE NOCASE"
                "    OR ei.description LIKE ? COLLATE NOCASE"
                "    OR ei.notes       LIKE ? COLLATE NOCASE)))"
            )
            params.extend([like, like, like, like])
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        return conn.execute(
            f"""SELECT inv.*
                FROM ExpenseInvoices inv
                {where}
                ORDER BY inv.expense_datetime DESC, inv.id DESC""",
            params,
        ).fetchall()
    finally:
        conn.close()
