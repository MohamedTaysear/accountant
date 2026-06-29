import expenses_db


def get_next_invoice_number() -> str:
    return expenses_db.get_next_invoice_number()


def validate_expense_item(category: str, amount) -> list:
    errors = []
    if not str(category).strip():
        errors.append("Category is required.")
    try:
        if float(amount) <= 0:
            errors.append("Amount must be greater than zero.")
    except (TypeError, ValueError):
        errors.append("Amount must be a valid number greater than zero.")
    return errors


def save_expense_invoice(expense_datetime: str, items: list) -> str:
    if not items:
        raise ValueError("Invoice must have at least one expense line.")
    return expenses_db.insert_expense_invoice(expense_datetime, items)


def delete_expense_invoice(invoice_id: int) -> None:
    expenses_db.delete_expense_invoice(invoice_id)


def get_expense_invoices(start_date=None, end_date=None, search=None) -> list:
    return expenses_db.get_all_expense_invoices(start_date, end_date, search)


def get_expense_invoice_by_id(invoice_id: int):
    return expenses_db.get_expense_invoice_by_id(invoice_id)


def get_expense_items_by_invoice(invoice_id: int) -> list:
    return expenses_db.get_expense_items_by_invoice(invoice_id)


def get_categories() -> list:
    return expenses_db.get_distinct_categories()


def get_expenses_for_report(start_date=None, end_date=None,
                            category=None, search=None) -> list:
    return expenses_db.get_expenses_for_report(start_date, end_date, category, search)
