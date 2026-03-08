"""
ShopFlow - Inventory Manager Module
Handles stock checks, reservations, and low-stock alerts.

Author: Team ShopFlow
Version: 1.0.0
"""


class InventoryManager:
    """
    Manages product inventory state.

    Responsibilities:
      - Check available stock (total minus reserved)
      - Reserve stock for pending orders
      - Release stock when orders are cancelled
      - Flag products that need reordering
    """

    def __init__(self, products: list):
        """
        Initialize with the product list from products.json.

        Args:
            products: List of product dicts from the 'products' key
        """
        self.products = {p["id"]: p for p in products}

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def get_available_stock(self, product_id: str) -> int:
        """
        Return the number of units available for purchase.
        Available = total stock - reserved units.
        """
        product = self.products.get(product_id)
        if not product:
            print(f"WARNING: Product '{product_id}' not found in inventory.")
            return -1

        inventory = product["inventory"]
        return inventory["stock"] - inventory["reserved"]

    def check_availability(self, product_id: str, quantity: int) -> bool:
        """Check if the requested quantity is currently available."""
        available = self.get_available_stock(product_id)
        if available < 0:
            return False
        if available < quantity:
            print(f"Not enough stock for '{product_id}'. "
                  f"Requested: {quantity}, Available: {available}")
            return False
        return True

    # ------------------------------------------------------------------
    # Reservations
    # ------------------------------------------------------------------

    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Reserve units for a pending order."""
        if not self.check_availability(product_id, quantity):
            return False
        self.products[product_id]["inventory"]["reserved"] += quantity
        print(f"Reserved {quantity} unit(s) of '{product_id}'.")
        return True

    def release_stock(self, product_id: str, quantity: int) -> bool:
        """Release previously reserved units (e.g. order cancellation)."""
        product = self.products.get(product_id)
        if not product:
            return False
        current_reserved = product["inventory"]["reserved"]
        if quantity > current_reserved:
            print(f"Cannot release {quantity} — only {current_reserved} reserved.")
            return False
        product["inventory"]["reserved"] -= quantity
        print(f"Released {quantity} unit(s) of '{product_id}'.")
        return True

    def fulfill_order(self, product_id: str, quantity: int) -> bool:
        """Deduct sold units from stock after order fulfillment."""
        product = self.products.get(product_id)
        if not product:
            return False
        inventory = product["inventory"]
        if inventory["reserved"] < quantity:
            print(f"Cannot fulfill — only {inventory['reserved']} units reserved.")
            return False
        inventory["stock"] -= quantity
        inventory["reserved"] -= quantity
        print(f"Fulfilled {quantity} unit(s) of '{product_id}'. "
              f"Remaining stock: {inventory['stock']}")
        return True

    # ------------------------------------------------------------------
    # Reports & Alerts
    # ------------------------------------------------------------------

    def get_low_stock_alerts(self) -> list:
        """Return products at or below their reorder level."""
        alerts = []
        for product_id, product in self.products.items():
            inv = product["inventory"]
            if inv["stock"] <= inv["reorder_level"]:
                alerts.append({
                    "product_id":    product_id,
                    "product_name":  product["name"],
                    "current_stock": inv["stock"],
                    "reorder_level": inv["reorder_level"],
                    "reorder_qty":   inv["reorder_qty"]
                })
        if not alerts:
            print("All products are above reorder levels.")
        else:
            print(f"{len(alerts)} product(s) need restocking.")
        return alerts

    def get_inventory_report(self) -> dict:
        """Generate a full inventory summary report."""
        report = {
            "total_products":  len(self.products),
            "total_units":     0,
            "total_reserved":  0,
            "total_available": 0,
            "low_stock_count": 0,
            "products":        []
        }
        for product_id, product in self.products.items():
            inv = product["inventory"]
            available = inv["stock"] - inv["reserved"]
            is_low = inv["stock"] <= inv["reorder_level"]

            report["total_units"]     += inv["stock"]
            report["total_reserved"]  += inv["reserved"]
            report["total_available"] += available
            if is_low:
                report["low_stock_count"] += 1

            report["products"].append({
                "id":        product_id,
                "name":      product["name"],
                "stock":     inv["stock"],
                "reserved":  inv["reserved"],
                "available": available,
                "low_stock": is_low
            })
        return report
