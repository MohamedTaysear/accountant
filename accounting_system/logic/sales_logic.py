import sales_db
import products_db


def get_next_invoice_number() -> str:
    return sales_db.get_next_invoice_number()


def calculate_subtotal(quantity: float, unit_price: float) -> float:
    return round(quantity * unit_price, 10)


def calculate_total(items: list, discount: float) -> float:
    subtotal = sum(item["subtotal"] for item in items)
    return max(0.0, subtotal - discount)


def validate_line(quantity: float, unit_price: float) -> tuple:
    if quantity <= 0:
        return False, "Quantity must be greater than 0."
    if unit_price < 0:
        return False, "Unit price cannot be negative."
    return True, ""


def validate_stock(product_id: int, quantity: float, current_items: list) -> tuple:
    already_queued = sum(
        item["quantity"] for item in current_items
        if item["product_id"] == product_id
    )
    rows = products_db.get_active_products()
    product = next((r for r in rows if r["id"] == product_id), None)
    if product is None:
        return False, "Product is not available."
    effective_available = product["stock_quantity"] - already_queued
    if quantity > effective_available:
        return False, (
            f"Insufficient stock. Available: {effective_available}, "
            f"Requested: {quantity}."
        )
    return True, ""


def save_sale(customer_name, discount_amount: float, items: list) -> str:
    if not items:
        raise ValueError("Invoice must have at least one item before saving.")
    subtotal = sum(item["subtotal"] for item in items)
    if discount_amount > subtotal:
        raise ValueError(
            f"Discount ({discount_amount}) cannot exceed invoice subtotal ({subtotal})."
        )
    customer = customer_name.strip() if customer_name else None
    return sales_db.insert_sale_with_items(customer, discount_amount, items)


def void_sale(sale_id: int) -> None:
    sale = sales_db.get_sale_by_id(sale_id)
    if sale is None:
        raise ValueError("Sale not found.")
    if sale["status"] == "voided":
        raise ValueError("This invoice has already been voided.")
    sales_db.void_sale(sale_id)
