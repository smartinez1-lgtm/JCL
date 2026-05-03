"""Template helpers for cart totals shown in the navbar."""
from decimal import Decimal

from .forms import THEME_CHOICES


def cart_summary(request):
    """Expose cart item count and grand total to all templates."""
    cart = request.session.get("cart", {})
    count = 0
    total = Decimal("0.00")

    for cart_item in cart.values():
        quantity = int(cart_item.get("quantity", 0))
        price = Decimal(str(cart_item.get("price", "0.00")))
        count += quantity
        total += price * quantity

    return {
        "cart_items_count": count,
        "cart_total_amount": total,
    }


def theme_settings(request):
    """Expose the active theme name to every template."""
    allowed_themes = {theme for theme, _ in THEME_CHOICES}
    active_theme = request.session.get("site_theme", "pink")

    if active_theme not in allowed_themes:
        active_theme = "pink"

    return {"active_theme": active_theme}
