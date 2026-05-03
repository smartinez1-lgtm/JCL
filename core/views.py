"""Views for dashboard, inventory CRUD, cashier, and receipts."""
import os
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Count, DecimalField, IntegerField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdminSetupForm, CartAddForm, CartUpdateForm, ItemForm, SearchForm, SignUpForm, ThemeSettingsForm
from .models import Branch, Item, Transaction, TransactionItem


def _is_admin_user(user):
    """Allow only staff/admin users into management-only pages."""
    return user.is_authenticated and user.is_staff


def _get_cart(session):
    """Return the session cart, creating it when missing."""
    cart = session.setdefault("cart", {})
    session.modified = True
    return cart


def signup_view(request):
    """Create a user account and sign the user in immediately."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                form.add_error("username", "That username is already taken. Please choose another one.")
            else:
                login(request, user)
                messages.success(request, "Account created successfully. You are now signed in.")
                return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


def setup_admin_view(request):
    """Temporary protected route for creating the first production admin."""
    setup_key = os.environ.get("SETUP_ADMIN_KEY", "")
    provided_key = request.GET.get("key", "")

    if not setup_key:
        raise Http404("Admin setup is disabled.")
    if provided_key != setup_key:
        return HttpResponseForbidden("Invalid setup key.")

    if request.method == "POST":
        form = AdminSetupForm(request.POST)
        if form.is_valid():
            user_model = get_user_model()
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user, created = user_model.objects.get_or_create(username=username)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            messages.success(
                request,
                f"Admin account {'created' if created else 'updated'} successfully. You can log in now.",
            )
            return redirect("login")
    else:
        form = AdminSetupForm()

    return render(request, "registration/setup_admin.html", {"form": form, "setup_key": provided_key})


def _cart_details(session):
    """Build a template-friendly cart summary with totals."""
    cart = session.get("cart", {})
    item_ids = [int(item_id) for item_id in cart.keys()]
    items = Item.objects.filter(id__in=item_ids)
    items_by_id = {item.id: item for item in items}

    lines = []
    total = Decimal("0.00")
    total_quantity = 0

    for item_id, entry in cart.items():
        item = items_by_id.get(int(item_id))
        if not item:
            continue

        quantity = int(entry["quantity"])
        price = Decimal(str(entry["price"]))
        subtotal = price * quantity
        total += subtotal
        total_quantity += quantity
        lines.append(
            {
                "item": item,
                "quantity": quantity,
                "price": price,
                "subtotal": subtotal,
                "update_form": CartUpdateForm(initial={"quantity": quantity}),
            }
        )

    return {
        "lines": lines,
        "total": total,
        "total_quantity": total_quantity,
    }


@login_required
def dashboard_view(request):
    """Show quick summary cards for inventory and cashier activity."""
    if not request.user.is_staff:
        return redirect("cashier")

    items = Item.objects.select_related("branch").all()
    branch_transaction_totals = Transaction.objects.filter(branch=OuterRef("pk")).values("branch").annotate(
        total=Sum("total_amount")
    )
    branch_units_sold = TransactionItem.objects.filter(transaction__branch=OuterRef("pk")).values(
        "transaction__branch"
    ).annotate(total=Sum("quantity"))
    low_stock_count = items.filter(quantity__lt=5).count()
    total_stock = items.aggregate(total=Sum("quantity"))["total"] or 0
    total_items = items.count()
    transaction_count = Transaction.objects.aggregate(total=Count("id"))["total"] or 0
    total_sales = Transaction.objects.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

    context = {
        "branch_count": Branch.objects.filter(is_active=True).count(),
        "branch_sales": Branch.objects.annotate(
            item_count=Count("items", distinct=True),
            transaction_count=Count("transactions", distinct=True),
            total_sales=Coalesce(
                Subquery(branch_transaction_totals.values("total")[:1]),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
            units_sold=Coalesce(
                Subquery(branch_units_sold.values("total")[:1]),
                Value(0),
                output_field=IntegerField(),
            ),
        ),
        "total_items": total_items,
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
        "transaction_count": transaction_count,
        "total_sales": total_sales,
        "recent_transactions": Transaction.objects.select_related("branch").prefetch_related(
            "transaction_items",
            "transaction_items__item",
        )[:5],
        "low_stock_items": items.filter(quantity__lt=5)[:5],
    }
    return render(request, "core/dashboard.html", context)


@login_required
def settings_view(request):
    """Let each signed-in user choose the website theme for their session."""
    if request.method == "POST":
        form = ThemeSettingsForm(request.POST)
        if form.is_valid():
            request.session["site_theme"] = form.cleaned_data["theme"]
            request.session.modified = True
            messages.success(request, "Theme updated successfully.")
            return redirect("settings")
    else:
        form = ThemeSettingsForm(initial={"theme": request.session.get("site_theme", "pink")})

    return render(request, "core/settings.html", {"form": form})


@login_required
@user_passes_test(_is_admin_user)
def inventory_list_view(request):
    """List inventory items and optionally filter them by search term."""
    form = SearchForm(request.GET)
    items = Item.objects.select_related("branch").all()

    if form.is_valid():
        query = form.cleaned_data["q"]
        if query:
            items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    context = {
        "items": items,
        "search_form": form,
    }
    return render(request, "core/inventory_list.html", context)


@login_required
@user_passes_test(_is_admin_user)
def item_create_view(request):
    """Create a new item and return to the inventory list on success."""
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item added successfully.")
            return redirect("inventory_list")
    else:
        form = ItemForm()

    return render(
        request,
        "core/item_form.html",
        {"form": form, "page_title": "Add Item", "button_label": "Save Item"},
    )


@login_required
@user_passes_test(_is_admin_user)
def item_update_view(request, pk):
    """Edit an existing item."""
    item = get_object_or_404(Item, pk=pk)

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully.")
            return redirect("inventory_list")
    else:
        form = ItemForm(instance=item)

    return render(
        request,
        "core/item_form.html",
        {
            "form": form,
            "page_title": f"Edit {item.name}",
            "button_label": "Update Item",
            "item": item,
        },
    )


@login_required
@user_passes_test(_is_admin_user)
def item_delete_view(request, pk):
    """Confirm and delete an item."""
    item = get_object_or_404(Item, pk=pk)

    if request.method == "POST":
        item.sales.update(item_name=item.name, item_price=item.price)
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect("inventory_list")

    return render(request, "core/item_confirm_delete.html", {"item": item})


@login_required
def cashier_view(request):
    """Show sellable items together with the current cart."""
    search_form = SearchForm(request.GET)
    items = Item.objects.select_related("branch").filter(quantity__gt=0, branch__is_active=True)

    if search_form.is_valid():
        query = search_form.cleaned_data["q"]
        if query:
            items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    cart = _cart_details(request.session)
    add_forms = {item.id: CartAddForm(initial={"quantity": 1}) for item in items}
    cart_item_ids = {line["item"].id for line in cart["lines"]}

    context = {
        "items": items,
        "search_form": search_form,
        "cart": cart,
        "add_forms": add_forms,
        "cart_item_ids": cart_item_ids,
    }
    return render(request, "core/cashier.html", context)


@login_required
def add_to_cart_view(request, item_id):
    """Add an item to the session cart while respecting available stock."""
    item = get_object_or_404(Item, pk=item_id)

    if request.method != "POST":
        return redirect("cashier")

    form = CartAddForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Enter a valid quantity to add.")
        return redirect("cashier")

    quantity = form.cleaned_data["quantity"]
    cart = _get_cart(request.session)
    existing_quantity = int(cart.get(str(item.id), {}).get("quantity", 0))
    requested_quantity = existing_quantity + quantity

    if requested_quantity > item.quantity:
        messages.error(request, f"Only {item.quantity} unit(s) of {item.name} are available.")
        return redirect("cashier")

    cart[str(item.id)] = {
        "name": item.name,
        "price": str(item.price),
        "quantity": requested_quantity,
    }
    request.session.modified = True
    messages.success(request, f"{item.name} added to cart.")
    return redirect("cashier")


@login_required
def add_multiple_to_cart_view(request):
    """Add several items to the cart from a single cashier form submit."""
    if request.method != "POST":
        return redirect("cashier")

    items = Item.objects.select_related("branch").filter(quantity__gt=0, branch__is_active=True)
    cart = _get_cart(request.session)
    added_count = 0
    errors = []

    for item in items:
        raw_quantity = request.POST.get(f"qty_{item.id}", "").strip()
        if not raw_quantity:
            continue

        try:
            quantity = int(raw_quantity)
        except ValueError:
            errors.append(f"{item.name}: quantity must be a whole number.")
            continue

        if quantity < 0:
            errors.append(f"{item.name}: quantity cannot be negative.")
            continue

        if quantity == 0:
            continue

        existing_quantity = int(cart.get(str(item.id), {}).get("quantity", 0))
        requested_quantity = existing_quantity + quantity
        if requested_quantity > item.quantity:
            errors.append(f"{item.name}: only {item.quantity} unit(s) available.")
            continue

        cart[str(item.id)] = {
            "name": item.name,
            "price": str(item.price),
            "quantity": requested_quantity,
        }
        added_count += 1

    request.session.modified = True

    if added_count:
        messages.success(request, f"Added {added_count} item type(s) to the cart.")
    if errors:
        for error in errors[:5]:
            messages.error(request, error)
    if not added_count and not errors:
        messages.error(request, "Enter a quantity for at least one item.")

    return redirect("cashier")


@login_required
def update_cart_view(request, item_id):
    """Update quantity of a cart line while checking remaining stock."""
    if request.method != "POST":
        return redirect("cashier")

    item = get_object_or_404(Item, pk=item_id)
    form = CartUpdateForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Enter a valid quantity.")
        return redirect("cashier")

    quantity = form.cleaned_data["quantity"]
    if quantity > item.quantity:
        messages.error(request, f"Only {item.quantity} unit(s) of {item.name} are available.")
        return redirect("cashier")

    cart = _get_cart(request.session)
    if str(item.id) in cart:
        cart[str(item.id)]["quantity"] = quantity
        request.session.modified = True
        messages.success(request, f"{item.name} quantity updated.")

    return redirect("cashier")


@login_required
def remove_from_cart_view(request, item_id):
    """Remove a line item from the cart."""
    cart = _get_cart(request.session)
    removed = cart.pop(str(item_id), None)
    request.session.modified = True

    if removed:
        messages.success(request, f"{removed['name']} removed from cart.")

    return redirect("cashier")


@login_required
def checkout_view(request):
    """Turn the current cart into a saved transaction and deduct stock."""
    if request.method != "POST":
        return redirect("cashier")

    cart_data = _cart_details(request.session)
    if not cart_data["lines"]:
        messages.error(request, "Cannot checkout an empty cart.")
        return redirect("cashier")

    with transaction.atomic():
        first_line = cart_data["lines"][0]
        transaction_record = Transaction.objects.create(
            branch=first_line["item"].branch,
            total_amount=Decimal("0.00"),
        )
        total_amount = Decimal("0.00")

        for line in cart_data["lines"]:
            item = Item.objects.select_for_update().get(pk=line["item"].pk)
            quantity = line["quantity"]

            if quantity > item.quantity:
                messages.error(
                    request,
                    f"Checkout failed. {item.name} only has {item.quantity} unit(s) left in stock.",
                )
                transaction.set_rollback(True)
                return redirect("cashier")

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

    request.session["cart"] = {}
    request.session.modified = True
    messages.success(request, f"Checkout completed. Transaction #{transaction_record.pk} saved.")
    return redirect("receipt", transaction_id=transaction_record.pk)


@login_required
def receipt_view(request, transaction_id):
    """Display a simple printable receipt."""
    transaction_record = get_object_or_404(
        Transaction.objects.select_related("branch").prefetch_related("transaction_items", "transaction_items__item"),
        pk=transaction_id,
    )
    return render(request, "core/receipt.html", {"transaction": transaction_record})
