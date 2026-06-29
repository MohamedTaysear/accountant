import purchases_db
import products_db


def validate_line(quantity: float, unit_price: float) -> tuple:
    if quantity <= 0:
        return False, "Quantity must be greater than 0."
    if unit_price < 0:
        return False, "Unit price cannot be negative."
    return True, ""


def calculate_subtotal(quantity: float, unit_price: float) -> float:
    return round(quantity * unit_price, 2)


def calculate_total(items: list) -> float:
    return round(sum(item["subtotal"] for item in items), 2)


def get_next_invoice_number() -> str:
    return purchases_db.get_next_invoice_number()


def save_purchase(supplier_name, items: list) -> str:
    if not items:
        raise ValueError("Invoice must have at least one item before saving.")
    return purchases_db.insert_purchase_with_items(supplier_name, items)


def check_void_stock(purchase_id: int) -> tuple:
    items = purchases_db.get_purchase_items(purchase_id)
    for item in items:
        product = products_db.get_product_by_id(item["product_id"])
        if product is None:
            continue
        if product["stock_quantity"] < item["quantity"]:
            return (
                False,
                f"Cannot void: insufficient stock for '{item['product_name']}'. "
                f"Available: {product['stock_quantity']}, "
                f"Required: {item['quantity']}. "
                f"Some of this stock may have already been sold."
            )
    return True, ""


def void_purchase(purchase_id: int) -> None:
    ok, msg = check_void_stock(purchase_id)
    if not ok:
        raise ValueError(msg)
    purchases_db.void_purchase(purchase_id)
