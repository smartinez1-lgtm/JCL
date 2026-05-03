"""Database models for inventory and cashier transactions."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Item(models.Model):
    """Stores inventory details for a single sellable item."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        """Block negative stock and price values before saving."""
        if self.quantity < 0:
            raise ValidationError({"quantity": "Quantity cannot be negative."})
        if self.price < Decimal("0.00"):
            raise ValidationError({"price": "Price cannot be negative."})

    @property
    def is_low_stock(self):
        """Helper used by templates and admin for low-stock warnings."""
        return self.quantity < 5


class Transaction(models.Model):
    """Represents one completed cashier checkout."""

    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Transaction #{self.pk}"


class TransactionItem(models.Model):
    """Stores each line item included in a transaction."""

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="transaction_items",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sales",
    )
    item_name = models.CharField(max_length=150, blank=True)
    item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.display_item_name} x {self.quantity}"

    @property
    def display_item_name(self):
        """Return the current item name or the saved receipt snapshot."""
        if self.item:
            return self.item.name
        return self.item_name or "Deleted item"

    @property
    def display_item_price(self):
        """Return the current item price or the saved receipt snapshot."""
        if self.item:
            return self.item.price
        return self.item_price

    def clean(self):
        """Protect against invalid sold quantities."""
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})
        if self.subtotal < Decimal("0.00"):
            raise ValidationError({"subtotal": "Subtotal cannot be negative."})
        if self.item_price < Decimal("0.00"):
            raise ValidationError({"item_price": "Item price cannot be negative."})
