from datetime import datetime
from .models import Category, ContactMessage


def global_context(request):
    cart = request.session.get("cart", [])
    cart_count = sum(item["qty"] for item in cart)
    wishlist = request.session.get("wishlist", [])

    unread_messages_count = 0
    if request.user.is_authenticated and request.user.is_staff:
        unread_messages_count = ContactMessage.objects.filter(is_read=False).count()

    return {
        "current_user": request.user if request.user.is_authenticated else None,
        "cart_count": cart_count,
        "wishlist_ids": set(wishlist),
        "wishlist_count": len(wishlist),
        "all_categories": list(Category.objects.order_by("display_order")),
        "current_year": datetime.now().year,
        "unread_messages_count": unread_messages_count,
    }
