"""Admin registrations for convenient backend management."""
from django.contrib import admin

from .models import Item, Transaction, TransactionItem


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "quantity", "is_low_stock", "date_added")
    list_filter = ("date_added",)
    search_fields = ("name", "description")
    readonly_fields = ("date_added",)


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ("item", "item_name", "item_price", "quantity", "subtotal")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "total_amount")
    readonly_fields = ("date", "total_amount")
    inlines = [TransactionItemInline]


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ("transaction", "display_item_name", "quantity", "subtotal")
    readonly_fields = ("transaction", "item", "item_name", "item_price", "quantity", "subtotal")
