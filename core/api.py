"""JSON API endpoints for inventory and cashier data."""
import json
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Branch, Item, Transaction, TransactionItem


def _error(message, status=400, errors=None):
    """Return a consistent JSON error response."""
    payload = {"error": message}
    if errors:
        payload["details"] = errors
    return JsonResponse(payload, status=status)


def _require_user(request):
    """Require an authenticated Django session for API access."""
    if request.user.is_authenticated:
        return None
    return _error("Authentication required.", status=401)


def _require_staff(request):
    """Require an authenticated staff user for admin-only API data."""
    auth_error = _require_user(request)
    if auth_error:
        return auth_error
    if not request.user.is_staff:
        return _error("Admin access required.", status=403)
    return None


def _require_cashier_user(request):
    """Require an authenticated user for cashier/cart API actions."""
    auth_error = _require_user(request)
    if auth_error:
        return auth_error
    return None


def _read_json(request):
    """Parse a JSON request body into a dictionary."""
    if not request.body:
        return {}

    try:
        data = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Request body must be valid JSON.")

    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")

    return data


def _decimal(value, field_name):
    """Convert API input into a Decimal with a readable validation error."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError({field_name: "Enter a valid number."})


def _integer(value, field_name):
    """Convert API input into an integer with a readable validation error."""
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError({field_name: "Enter a valid whole number."})


def _validation_details(error):
    """Serialize Django ValidationError details for JSON responses."""
    if hasattr(error, "message_dict"):
        return error.message_dict
    return {"non_field_errors": error.messages}


def _item_payload(item):
    """Serialize an Item model for API responses."""
    return {
        "id": item.id,
        "branch_id": item.branch_id,
        "branch": item.branch.name,
        "name": item.name,
        "description": item.description or "",
        "price": str(item.price),
        "quantity": item.quantity,
        "is_low_stock": item.is_low_stock,
        "date_added": item.date_added.isoformat(),
    }


def _transaction_payload(transaction):
    """Serialize a Transaction model with its line items."""
    return {
        "id": transaction.id,
        "branch_id": transaction.branch_id,
        "branch": transaction.branch.name,
        "date": transaction.date.isoformat(),
        "total_amount": str(transaction.total_amount),
        "items": [
            {
                "item_id": line.item_id,
                "name": line.display_item_name,
                "quantity": line.quantity,
                "price": str(line.display_item_price),
                "subtotal": str(line.subtotal),
            }
            for line in transaction.transaction_items.all()
        ],
    }


@require_http_methods(["GET", "POST"])
def api_items(request):
    """List inventory items or create a new item."""
    auth_error = _require_user(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        query = request.GET.get("q", "").strip()
        items = Item.objects.select_related("branch").all()
        if query:
            items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return JsonResponse({"items": [_item_payload(item) for item in items]})

    try:
        staff_error = _require_staff(request)
        if staff_error:
            return staff_error

        data = _read_json(request)
        branch = None
        if data.get("branch_id"):
            branch = Branch.objects.get(pk=_integer(data.get("branch_id"), "branch_id"))
        item = Item(
            branch=branch or Branch.objects.get_or_create(name="Main Branch")[0],
            name=data.get("name", ""),
            description=data.get("description", ""),
            price=_decimal(data.get("price"), "price"),
            quantity=_integer(data.get("quantity", 0), "quantity"),
        )
        item.full_clean()
        item.save()
    except ValueError as error:
        return _error(str(error))
    except Branch.DoesNotExist:
        return _error("Branch not found.", status=404)
    except ValidationError as error:
        return _error("Item validation failed.", errors=_validation_details(error))

    return JsonResponse({"item": _item_payload(item)}, status=201)


@require_http_methods(["GET", "PATCH", "DELETE"])
def api_item_detail(request, item_id):
    """Retrieve, update, or delete one inventory item."""
    auth_error = _require_user(request)
    if auth_error:
        return auth_error

    try:
        item = Item.objects.select_related("branch").get(pk=item_id)
    except Item.DoesNotExist:
        return _error("Item not found.", status=404)

    if request.method == "GET":
        return JsonResponse({"item": _item_payload(item)})

    staff_error = _require_staff(request)
    if staff_error:
        return staff_error

    if request.method == "DELETE":
        item.sales.update(item_name=item.name, item_price=item.price)
        item.delete()
        return JsonResponse({}, status=204)

    try:
        data = _read_json(request)
        if "name" in data:
            item.name = data["name"]
        if "description" in data:
            item.description = data["description"]
        if "branch_id" in data:
            item.branch = Branch.objects.get(pk=_integer(data["branch_id"], "branch_id"))
        if "price" in data:
            item.price = _decimal(data["price"], "price")
        if "quantity" in data:
            item.quantity = _integer(data["quantity"], "quantity")
        item.full_clean()
        item.save()
    except ValueError as error:
        return _error(str(error))
    except Branch.DoesNotExist:
        return _error("Branch not found.", status=404)
    except ValidationError as error:
        return _error("Item validation failed.", errors=_validation_details(error))

    return JsonResponse({"item": _item_payload(item)})


@require_http_methods(["GET"])
def api_transactions(request):
    """List saved cashier transactions."""
    auth_error = _require_staff(request)
    if auth_error:
        return auth_error

    transactions = Transaction.objects.select_related("branch").prefetch_related(
        "transaction_items",
        "transaction_items__item",
    )[:50]
    return JsonResponse({"transactions": [_transaction_payload(transaction) for transaction in transactions]})


@require_http_methods(["POST"])
def api_checkout(request):
    """Create a transaction directly from JSON line items and deduct stock."""
    auth_error = _require_cashier_user(request)
    if auth_error:
        return auth_error

    try:
        data = _read_json(request)
    except ValueError as error:
        return _error(str(error))

    lines = data.get("items", [])
    if not isinstance(lines, list) or not lines:
        return _error("Provide an items list with item_id and quantity values.")

    try:
        requested = [
            {
                "item_id": _integer(line.get("item_id"), "item_id"),
                "quantity": _integer(line.get("quantity"), "quantity"),
            }
            for line in lines
            if isinstance(line, dict)
        ]
    except ValidationError as error:
        return _error("Checkout validation failed.", errors=_validation_details(error))

    if len(requested) != len(lines):
        return _error("Each checkout line must be a JSON object.")

    if any(line["quantity"] <= 0 for line in requested):
        return _error("Each checkout quantity must be greater than zero.")

    with db_transaction.atomic():
        item_ids = [line["item_id"] for line in requested]
        items_by_id = {
            item.id: item
            for item in Item.objects.select_for_update().select_related("branch").filter(id__in=item_ids)
        }

        missing_ids = sorted(set(item_ids) - set(items_by_id.keys()))
        if missing_ids:
            return _error("One or more items were not found.", status=404, errors={"item_ids": missing_ids})

        first_item = items_by_id[requested[0]["item_id"]]
        transaction_record = Transaction.objects.create(
            branch=first_item.branch,
            total_amount=Decimal("0.00"),
        )
        total_amount = Decimal("0.00")

        for line in requested:
            item = items_by_id[line["item_id"]]
            quantity = line["quantity"]

            if quantity > item.quantity:
                db_transaction.set_rollback(True)
                return _error(
                    f"{item.name} only has {item.quantity} unit(s) available.",
                    status=409,
                )

            subtotal = item.price * quantity
            TransactionItem.objects.create(
                transaction=transaction_record,
                item=item,
                item_name=item.name,
                item_price=item.price,
                quantity=quantity,
                subtotal=subtotal,
            )

            item.quantity -= quantity
            item.full_clean()
            item.save()
            total_amount += subtotal

        transaction_record.total_amount = total_amount
        transaction_record.save()

    transaction_record = Transaction.objects.select_related("branch").prefetch_related(
        "transaction_items",
        "transaction_items__item",
    ).get(pk=transaction_record.pk)
    return JsonResponse({"transaction": _transaction_payload(transaction_record)}, status=201)
