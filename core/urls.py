"""App level URL patterns for inventory and cashier pages."""
from django.urls import path

from . import api
from . import views


urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("setup-admin/", views.setup_admin_view, name="setup_admin"),
    path("api/items/", api.api_items, name="api_items"),
    path("api/items/<int:item_id>/", api.api_item_detail, name="api_item_detail"),
    path("api/transactions/", api.api_transactions, name="api_transactions"),
    path("api/checkout/", api.api_checkout, name="api_checkout"),
    path("branches/", views.branch_list_view, name="branch_list"),
    path("branches/add/", views.branch_create_view, name="branch_create"),
    path("branches/<int:pk>/", views.branch_detail_view, name="branch_detail"),
    path("branches/<int:pk>/edit/", views.branch_update_view, name="branch_update"),
    path("branches/<int:pk>/delete/", views.branch_delete_view, name="branch_delete"),
    path("users/", views.user_management_view, name="user_management"),
    path("users/<int:user_id>/branch/", views.set_user_branch_view, name="set_user_branch"),
    path("users/<int:user_id>/approve/", views.approve_user_view, name="approve_user"),
    path("users/<int:user_id>/deny/", views.deny_user_view, name="deny_user"),
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
