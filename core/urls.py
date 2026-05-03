"""App level URL patterns for inventory and cashier pages."""
from django.urls import path

from . import api
from . import views


urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("api/items/", api.api_items, name="api_items"),
    path("api/items/<int:item_id>/", api.api_item_detail, name="api_item_detail"),
    path("api/transactions/", api.api_transactions, name="api_transactions"),
    path("api/checkout/", api.api_checkout, name="api_checkout"),
    path("inventory/", views.inventory_list_view, name="inventory_list"),
    path("inventory/add/", views.item_create_view, name="item_create"),
    path("inventory/<int:pk>/edit/", views.item_update_view, name="item_update"),
    path("inventory/<int:pk>/delete/", views.item_delete_view, name="item_delete"),
    path("settings/", views.settings_view, name="settings"),
    path("cashier/", views.cashier_view, name="cashier"),
    path("cashier/add-multiple/", views.add_multiple_to_cart_view, name="add_multiple_to_cart"),
    path("cashier/add/<int:item_id>/", views.add_to_cart_view, name="add_to_cart"),
    path("cashier/update/<int:item_id>/", views.update_cart_view, name="update_cart"),
    path("cashier/remove/<int:item_id>/", views.remove_from_cart_view, name="remove_from_cart"),
    path("cashier/checkout/", views.checkout_view, name="checkout"),
    path("receipt/<int:transaction_id>/", views.receipt_view, name="receipt"),
]
