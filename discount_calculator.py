"""
ShopFlow - Discount Calculator Module
Handles loyalty, bulk, and seasonal discount logic.

Author: Team ShopFlow
Version: 1.0.0
"""


class DiscountCalculator:
    """
    Calculates discounts based on rules defined in config.json.

    Supports:
      - Loyalty tier discounts (bronze, silver, gold, platinum)
      - Bulk purchase discounts
      - Seasonal promotions (when enabled)
    """

    def __init__(self, pricing_config: dict):
        """
        Initialize with the 'pricing' block from config.json.

        Args:
            pricing_config: dict containing discount_rules, tax_rate, currency
        """
        self.config = pricing_config
        self.discount_rules = pricing_config["discount_rules"]

    # ------------------------------------------------------------------
    # Loyalty Discounts
    # ------------------------------------------------------------------

    def get_loyalty_discount(self, tier: str) -> float:
        """
        Return the discount percentage for a given loyalty tier.

        Args:
            tier: One of 'bronze', 'silver', 'gold', 'platinum'

        Returns:
            Discount as a decimal (e.g., 0.10 for 10%)
        """
        loyalty_rules = self.discount_rules["loyalty"]
        tier = tier.lower()

        if tier not in loyalty_rules:
            print(f"ERROR: Tier '{tier}' is invalid. Valid tiers: {list(loyalty_rules.keys())}")
            print(f"Falling back to bronze tier discount.")
            return loyalty_rules["bronze"]["discount_pct"]

        discount = loyalty_rules[tier]["discount_pct"]
        print(f"Loyalty tier '{tier}': {discount * 100:.0f}% discount applied.")
        return discount

    def get_tier_for_customer(self, purchase_count: int) -> str:
        """
        Determine a customer's loyalty tier based on purchase history.

        Args:
            purchase_count: Total number of completed purchases

        Returns:
            Tier name as a string
        """
        loyalty_rules = self.discount_rules["loyalty"]

        sorted_tiers = sorted(
            loyalty_rules.items(),
            key=lambda x: x[1]["min_purchases"],
            reverse=True
        )

        for tier_name, rules in sorted_tiers:
            if purchase_count >= rules["min_purchases"]:
                return tier_name

        return "none"

    # ------------------------------------------------------------------
    # Bulk Discounts
    # ------------------------------------------------------------------

    def get_bulk_discount(self, quantity: int) -> float:
        """
        Return the bulk discount for a given quantity ordered.

        Args:
            quantity: Number of units in the order

        Returns:
            Discount as a decimal (e.g., 0.05 for 5%)
        """
        bulk_rules = self.discount_rules["bulk"]

        if not bulk_rules["enabled"]:
            return 0.0

        sorted_tiers = sorted(
            bulk_rules["tiers"],
            key=lambda x: x["min_qty"],
            reverse=True
        )

        for tier in sorted_tiers:
            if quantity >= tier["min_qty"]:
                discount = tier["discount_pct"]
                print(f"Bulk discount for qty {quantity}: {discount * 100:.0f}% applied.")
                return discount

        return 0.0

    # ------------------------------------------------------------------
    # Seasonal Discounts
    # ------------------------------------------------------------------

    def get_seasonal_discount(self, promo_key: str) -> float:
        """
        Return the seasonal discount if the promotion is active.

        Args:
            promo_key: e.g. 'black_friday' or 'christmas'

        Returns:
            Discount as a decimal, or 0.0 if not active
        """
        seasonal_rules = self.discount_rules["seasonal"]

        if not seasonal_rules["enabled"]:
            print("INFO: Seasonal promotions are currently disabled.")
            return 0.0

        if promo_key not in seasonal_rules:
            print(f"ERROR: Unknown promotion '{promo_key}'.")
            print(f"Available: {[k for k in seasonal_rules if k != 'enabled']}")
            return 0.0

        promo    = seasonal_rules[promo_key]
        discount = promo["discount_pct"]
        max_uses = promo["max_uses"]
        print(f"PROMO '{promo_key}': {discount * 100:.0f}% off (max {max_uses} uses).")
        return discount

    # ------------------------------------------------------------------
    # Apply Discount & Tax
    # ------------------------------------------------------------------

    def apply_discount(self, price: float, discount_pct: float) -> float:
        """Apply a discount percentage to a price."""
        if not (0.0 <= discount_pct <= 1.0):
            raise ValueError(f"Invalid discount: {discount_pct}. Must be 0–1.")
        return round(price * (1 - discount_pct), 2)

    def apply_tax(self, price: float) -> float:
        """Apply the configured tax rate to a price."""
        return round(price * (1 + self.config["tax_rate"]), 2)
