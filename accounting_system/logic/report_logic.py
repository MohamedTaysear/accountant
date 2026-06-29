import datetime

import sales_db
import purchases_db
import products_db
import expenses_db


def get_total_sales(start_date=None, end_date=None) -> float:
    return sales_db.get_total_sales_amount(start_date, end_date)


def get_total_purchases(start_date=None, end_date=None) -> float:
    return purchases_db.get_total_purchases_amount(start_date, end_date)


def get_total_profit(start_date=None, end_date=None) -> float:
    c = sales_db.get_profit_components(start_date, end_date)
    return round(c["revenue"] - c["cost"] - c["discount"], 2)


def get_recent_activity(limit: int = 10) -> list:
    return sales_db.get_recent_activity(limit)


def get_sales_for_report(start_date=None, end_date=None, search=None) -> list:
    return sales_db.get_all_sales(start_date, end_date, search)


def get_purchases_for_report(start_date=None, end_date=None, search=None) -> list:
    return purchases_db.get_all_purchases(start_date, end_date, search)


def get_top_selling_products(start_date=None, end_date=None) -> list:
    return sales_db.get_top_selling_products(start_date, end_date)


def get_top_purchased_products(start_date=None, end_date=None) -> list:
    return purchases_db.get_top_purchased_products(start_date, end_date)


def get_inventory_value() -> float:
    return products_db.get_inventory_value()


def get_potential_stock_profit() -> float:
    return products_db.get_potential_stock_profit()


def get_potential_sales_value() -> float:
    return products_db.get_potential_sales_value()


def get_low_stock_count() -> int:
    return products_db.get_low_stock_count()


def get_today_expenses() -> float:
    today = str(datetime.date.today())
    return expenses_db.get_total_expenses(today, today)


def get_this_month_expenses() -> float:
    today = datetime.date.today()
    first = str(today.replace(day=1))
    return expenses_db.get_total_expenses(first, str(today))


def get_net_profit() -> float:
    return round(get_total_profit() - expenses_db.get_total_expenses(), 2)


def get_total_expenses(start_date=None, end_date=None) -> float:
    return expenses_db.get_total_expenses(start_date, end_date)


def get_top_expense_categories(start_date=None, end_date=None) -> list:
    return expenses_db.get_top_expense_categories(start_date, end_date)


def get_net_profit_for_period(start_date=None, end_date=None) -> float:
    return round(
        get_total_profit(start_date, end_date) - get_total_expenses(start_date, end_date), 2
    )
