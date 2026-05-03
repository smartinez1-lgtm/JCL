"""Admin registrations for convenient backend management."""
from django.contrib import admin

from .models import Branch, Item, Transaction, TransactionItem, UserBranchAssignment


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "date_added")
    list_filter = ("is_active", "date_added")
    search_fields = ("name", "address")
    readonly_fields = ("date_added",)


@admin.register(UserBranchAssignment)
class UserBranchAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "date_assigned")
    list_filter = ("branch", "date_assigned")
    search_fields = ("user__username", "user__email", "branch__name")
    readonly_fields = ("date_assigned",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "branch", "price", "quantity", "is_low_stock", "date_added")
    list_filter = ("branch", "date_added")
    search_fields = ("name", "description")
    readonly_fields = ("date_added",)


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ("item", "item_name", "item_price", "quantity", "subtotal")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "branch", "date", "total_amount")
    list_filter = ("branch", "date")
    readonly_fields = ("date", "total_amount")
    inlines = [TransactionItemInline]


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ("transaction", "display_item_name", "quantity", "subtotal")
    readonly_fields = ("transaction", "item", "item_name", "item_price", "quantity", "subtotal")
