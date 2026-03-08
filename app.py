"""
ShopFlow - E-Commerce Application
Main entry point for the application.

Author: Team ShopFlow
Version: 1.0.0
"""

import json
import os

from discount_calculator import DiscountCalculator
from inventory_manager import InventoryManager

CONFIG_PATH   = "config.json"
PRODUCTS_PATH = "data/products.json"


def load_json(filepath: str) -> dict:
    """Load and return JSON data from a file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r") as f:
        return json.load(f)


def get_product_by_id(products: list, product_id: str) -> dict | None:
    """Look up a single product by its ID."""
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def display_product_summary(product: dict) -> None:
    """Print a formatted product summary to the console."""
    pricing   = product["pricing"]
    inventory = product["inventory"]
    ratings   = product["ratings"]

    price           = pricing["sale_price"] if pricing["sale_price"] else pricing["base_price"]
    available_stock = inventory["stock"] - inventory["reserved"]

    print(f"\n{'=' * 50}")
    print(f"  {product['name']}")
    print(f"  Brand  : {product['brand']}")
    print(f"  SKU    : {product['sku']}")
    print(f"  Price  : ${price:.2f}")
    print(f"  Stock  : {available_stock} units available")
    print(f"  Rating : {ratings['average']} stars ({ratings['total_reviews']} reviews)")
    print(f"  Tags   : {', '.join(product['tags'])}")
    print(f"{'=' * 50}\n")


def calculate_order_total(product: dict, quantity: int,
                          config: dict, customer_tier: str = "bronze") -> dict:
    """
    Calculate the final order total including discounts and tax.

    Args:
        product:       Product dict from products.json
        quantity:      Number of units being ordered
        config:        Loaded config dict
        customer_tier: Customer's loyalty tier

    Returns:
        Dict with full pricing breakdown
    """
    pricing_config = config["pricing"]
    calculator     = DiscountCalculator(pricing_config)

    base_price = product["pricing"]["base_price"]
    sale_price = product["pricing"]["sale_price"]
    unit_price = sale_price if sale_price else base_price

    loyalty_discount = calculator.get_loyalty_discount(customer_tier)
    bulk_discount    = calculator.get_bulk_discount(quantity)
    best_discount    = max(loyalty_discount, bulk_discount)

    subtotal        = unit_price * quantity
    discount_amount = subtotal * best_discount
    taxable_amount  = subtotal - discount_amount
    tax_amount      = taxable_amount * pricing_config["tax_rate"]
    total           = taxable_amount + tax_amount

    return {
        "product_id":      product["id"],
        "product_name":    product["name"],
        "unit_price":      unit_price,
        "quantity":        quantity,
        "subtotal":        round(subtotal, 2),
        "discount_pct":    best_discount,
        "discount_amount": round(discount_amount, 2),
        "tax_rate":        pricing_config["tax_rate"],
        "tax_amount":      round(tax_amount, 2),
        "total":           round(total, 2),
        "currency":        pricing_config["currency"]
    }


def check_shipping(order_total: float, config: dict) -> dict:
    """Determine shipping options available for this order."""
    shipping_config = config["shipping"]
    free_threshold  = shipping_config["free_shipping_threshold"]
    rates           = shipping_config["rates"]

    if order_total >= free_threshold:
        return {
            "free_shipping": True,
            "message":       f"Free shipping on orders over ${free_threshold:.2f}!",
            "options":       rates
        }
    return {
        "free_shipping": False,
        "message":       f"Add ${free_threshold - order_total:.2f} more for free shipping.",
        "options":       rates
    }


def run_demo():
    """Run a demo order flow to test the application."""
    print("\n ShopFlow Demo — Order Processing\n")

    config        = load_json(CONFIG_PATH)
    products_data = load_json(PRODUCTS_PATH)
    products      = products_data["products"]

    inventory = InventoryManager(products)
    product   = get_product_by_id(products, "PROD-001")

    if not product:
        print("Product not found.")
        return

    display_product_summary(product)

    qty_requested = 3
    if not inventory.check_availability(product["id"], qty_requested):
        print(f"Insufficient stock for {qty_requested} units.")
        return

    order = calculate_order_total(
        product=product,
        quantity=qty_requested,
        config=config,
        customer_tier="silver"
    )

    print("Order Summary:")
    for key, value in order.items():
        print(f"   {key:<20} : {value}")

    shipping = check_shipping(order["total"], config)
    print(f"\nShipping: {shipping['message']}")


if __name__ == "__main__":
    run_demo()
