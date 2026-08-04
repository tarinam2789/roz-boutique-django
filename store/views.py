from decimal import Decimal
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages as flash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import (
    Category, Product, ProductSize, ProductColor, ProductMedia,
    SizeGuide, SizeGuideRow,
    ShippingRule, ReturnPolicy,
    Order, OrderItem, ReturnRequest, ContactMessage, Review, InstagramPost,
)

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


def _size_sort_key(size_code):
    return SIZE_ORDER.index(size_code) if size_code in SIZE_ORDER else 99


def _cart_details(request):
    cart = request.session.get("cart", [])
    items = []
    subtotal = Decimal("0.00")
    for entry in cart:
        try:
            product = Product.objects.get(id=entry["product_id"])
        except Product.DoesNotExist:
            continue
        line_total = product.price * entry["qty"]
        subtotal += line_total
        items.append({
            "product": product,
            "size_code": entry["size_code"],
            "qty": entry["qty"],
            "line_total": line_total,
        })
    return items, subtotal


def _compute_shipping(country, subtotal):
    rule = ShippingRule.objects.filter(country=country).first()
    if not rule:
        rule = ShippingRule.objects.filter(country="Other").first()
    if not rule:
        return Decimal("0.00"), Decimal("100.00")
    if subtotal >= rule.free_shipping_threshold:
        return Decimal("0.00"), rule.free_shipping_threshold
    return rule.standard_price, rule.free_shipping_threshold


# --------------------------------------------------------------- public UI

def index(request):
    categories = list(Category.objects.order_by("display_order"))

    new_arrivals = Product.objects.filter(active=True, is_new_arrival=True).order_by("-created_at")[:8]
    best_sellers = Product.objects.filter(active=True, is_best_seller=True).order_by("-created_at")[:8]
    featured = Product.objects.filter(active=True, is_featured=True).order_by("-created_at")[:6]
    seasonal = Product.objects.filter(active=True).exclude(season__isnull=True).exclude(season="").order_by("-created_at")[:6]

    category_previews = {}
    for cat in categories:
        prods = list(Product.objects.filter(active=True, category=cat).order_by("-created_at")[:4])
        if prods:
            category_previews[cat.slug] = prods

    reviews = Review.objects.order_by("-id")[:6]
    instagram_posts = InstagramPost.objects.order_by("sort_order")[:8]

    return render(request, "index.html", {
        "new_arrivals": new_arrivals,
        "best_sellers": best_sellers,
        "featured": featured,
        "categories": categories,
        "category_previews": category_previews,
        "reviews": reviews,
        "instagram_posts": instagram_posts,
        "seasonal": seasonal,
    })


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    sort = request.GET.get("sort", "newest")
    order_field = "-created_at"
    if sort == "price_low":
        order_field = "price"
    elif sort == "price_high":
        order_field = "-price"

    if slug == "new-arrivals":
        products = Product.objects.filter(active=True).filter(
            models_Q_category_or_new(category)
        ).order_by(order_field)
    else:
        products = Product.objects.filter(active=True, category=category).order_by(order_field)

    return render(request, "category.html", {
        "category": category, "products": products, "sort": sort,
    })


def models_Q_category_or_new(category):
    from django.db.models import Q
    return Q(category=category) | Q(is_new_arrival=True)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    sizes = sorted(product.sizes.all(), key=lambda s: _size_sort_key(s.size_code))

    size_guide = SizeGuide.objects.filter(product=product).first()
    guide_rows = []
    if size_guide:
        guide_rows = sorted(size_guide.rows.all(), key=lambda r: _size_sort_key(r.size_code))

    reviews = product.reviews.order_by("-id")
    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    related = Product.objects.filter(active=True, category=product.category).exclude(id=product.id)[:4]
    return_policy = ReturnPolicy.objects.first()
    colors = product.colors.all()
    media = product.media.all()

    return render(request, "product.html", {
        "product": product, "sizes": sizes, "size_guide": size_guide,
        "guide_rows": guide_rows, "reviews": reviews, "avg_rating": avg_rating,
        "related": related, "return_policy": return_policy, "colors": colors,
        "media": media,
    })


def wishlist_toggle(request):
    product_id = int(request.POST["product_id"])
    wishlist = request.session.get("wishlist", [])
    product = Product.objects.filter(id=product_id).first()
    if product_id in wishlist:
        wishlist.remove(product_id)
        if product:
            flash.info(request, f"Removed {product.name} from your wishlist.")
    else:
        wishlist.append(product_id)
        if product:
            flash.success(request, f"Added {product.name} to your wishlist.")
    request.session["wishlist"] = wishlist
    request.session.modified = True
    return redirect(request.META.get("HTTP_REFERER", "index"))


def wishlist_page(request):
    wishlist = request.session.get("wishlist", [])
    products = Product.objects.filter(id__in=wishlist, active=True) if wishlist else []
    return render(request, "wishlist.html", {"products": products})


def search(request):
    q = request.GET.get("q", "").strip()
    products = []
    if q:
        from django.db.models import Q
        products = Product.objects.filter(active=True).filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(fabric__icontains=q)
        ).order_by("-created_at")
    return render(request, "search_results.html", {"query": q, "products": products})


def cart_add(request):
    product_id = int(request.POST["product_id"])
    size_code = request.POST["size_code"]
    qty = max(1, int(request.POST.get("qty", 1)))

    product = get_object_or_404(Product, id=product_id)
    valid_sizes = {s.size_code for s in product.sizes.filter(quantity__gt=0)}
    if size_code not in valid_sizes:
        flash.error(request, "Please select an available size.")
        return redirect(request.META.get("HTTP_REFERER", "index"))

    cart = request.session.get("cart", [])
    for item in cart:
        if item["product_id"] == product_id and item["size_code"] == size_code:
            item["qty"] += qty
            break
    else:
        cart.append({"product_id": product_id, "size_code": size_code, "qty": qty})
    request.session["cart"] = cart
    request.session.modified = True
    flash.success(request, f"Added {product.name} ({size_code}) to your bag.")
    return redirect("cart_page")


def cart_page(request):
    items, subtotal = _cart_details(request)
    return render(request, "cart.html", {"items": items, "subtotal": subtotal})


def cart_update(request):
    idx = int(request.POST["index"])
    qty = int(request.POST.get("qty", 1))
    cart = request.session.get("cart", [])
    if 0 <= idx < len(cart):
        if qty <= 0:
            cart.pop(idx)
        else:
            cart[idx]["qty"] = qty
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart_page")


def cart_remove(request):
    idx = int(request.POST["index"])
    cart = request.session.get("cart", [])
    if 0 <= idx < len(cart):
        cart.pop(idx)
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart_page")


def checkout(request):
    items, subtotal = _cart_details(request)
    if not items:
        flash.info(request, "Your bag is empty.")
        return redirect("index")

    countries = ShippingRule.objects.order_by("country")
    return_policy = ReturnPolicy.objects.first()
    country = request.POST.get("country") or request.GET.get("country", "United States")
    shipping_cost, free_threshold = _compute_shipping(country, subtotal)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()

        if not (full_name and address and city):
            flash.error(request, "Please complete your shipping details.")
            return render(request, "checkout.html", {
                "items": items, "subtotal": subtotal, "countries": countries,
                "shipping_cost": shipping_cost, "free_threshold": free_threshold,
                "selected_country": country, "return_policy": return_policy,
            })

        total = subtotal + shipping_cost
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status="Placed", subtotal=subtotal, shipping_cost=shipping_cost, total=total,
            country=country, full_name=full_name, address=address, city=city, postal_code=postal_code,
        )
        for item in items:
            OrderItem.objects.create(
                order=order, product=item["product"], product_name=item["product"].name,
                size_code=item["size_code"], quantity=item["qty"], price=item["product"].price,
            )
            ProductSize.objects.filter(product=item["product"], size_code=item["size_code"]).update(
                quantity=max(0, item["product"].sizes.get(size_code=item["size_code"]).quantity - item["qty"])
            )
        request.session["cart"] = []
        request.session.modified = True
        return redirect("order_confirmation", order_id=order.id)

    return render(request, "checkout.html", {
        "items": items, "subtotal": subtotal, "countries": countries,
        "shipping_cost": shipping_cost, "free_threshold": free_threshold,
        "selected_country": country, "return_policy": return_policy,
    })


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    return render(request, "order_confirmation.html", {"order": order, "order_items": order_items})


def newsletter_subscribe(request):
    email = request.POST.get("email", "").strip()
    if email:
        from .models import NewsletterSubscriber
        _, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if created:
            flash.success(request, "Welcome to the Roz Boutique garden — check your inbox soon.")
        else:
            flash.info(request, "You're already on our list!")
    return redirect(request.META.get("HTTP_REFERER", "index"))


# ------------------------------------------------------------ account area

def account_register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        if not (name and email and password):
            flash.error(request, "Please fill in all fields.")
            return render(request, "account/register.html")
        if User.objects.filter(username=email).exists():
            flash.error(request, "An account with this email already exists.")
            return render(request, "account/register.html")
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""
        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )
        login(request, user)
        flash.success(request, "Welcome to Roz Boutique.")
        return redirect("account_dashboard")
    return render(request, "account/register.html")


def account_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not User.objects.filter(username=email).exists():
            flash.error(request, "No account found with that email. Please check the email or create an account.")
            return render(request, "account/login.html")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            flash.success(request, "Signed in successfully.")
            nxt = request.GET.get("next")
            return redirect(nxt or "account_dashboard")

        flash.error(request, "Wrong email or password. Please try again.")
    return render(request, "account/login.html")


def account_logout(request):
    logout(request)
    return redirect("index")


def account_dashboard(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('account_login')}?next={reverse('account_dashboard')}")

    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    orders_with_items = []
    for order in orders:
        items = order.items.all()
        return_map = {}
        for item in items:
            rr = ReturnRequest.objects.filter(order_item=item).first()
            return_map[item.id] = rr
        orders_with_items.append({"order": order, "order_items": items, "returns": return_map})

    return_policy = ReturnPolicy.objects.first()
    return render(request, "account/dashboard.html", {
        "orders_with_items": orders_with_items, "return_policy": return_policy,
    })


def account_return_request(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    order_item_id = int(request.POST["order_item_id"])
    reason = request.POST.get("reason", "").strip()
    item = get_object_or_404(OrderItem, id=order_item_id)
    order = item.order
    if order.user_id != request.user.id:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    policy = ReturnPolicy.objects.first()
    deadline = order.created_at + timedelta(days=policy.window_days)
    if datetime.now(deadline.tzinfo) > deadline:
        flash.error(request, f"Sorry, the {policy.window_days}-day return window for this order has passed.")
        return redirect("account_dashboard")

    if ReturnRequest.objects.filter(order_item=item).exists():
        flash.info(request, "A return request already exists for this item.")
        return redirect("account_dashboard")

    ReturnRequest.objects.create(order_item=item, user=request.user, reason=reason, status="Pending")
    flash.success(request, "Return request submitted for admin review.")
    return redirect("account_dashboard")


def policies(request):
    return_policy = ReturnPolicy.objects.first()
    shipping_rules = ShippingRule.objects.order_by("country")
    return render(request, "policies.html", {"return_policy": return_policy, "shipping_rules": shipping_rules})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not (name and email and message):
            flash.error(request, "Please fill in your name, email, and message.")
            return render(request, "contact.html", {"form_data": request.POST})

        ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)

        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            try:
                send_mail(
                    subject=f"Roz Boutique contact form: {subject or 'New message'}",
                    message=(
                        f"New message from your Roz Boutique contact form.\n\n"
                        f"Name: {name}\nEmail: {email}\nSubject: {subject or '(no subject)'}\n\n"
                        f"Message:\n{message}\n\n---\nReply directly to this email to respond to {name}."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.NOTIFY_EMAIL],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"[email] Failed to send contact notification: {e}")

        flash.success(request, "Thank you — your message has been sent. We'll get back to you soon.")
        return redirect("contact")

    return render(request, "contact.html", {"form_data": {}})
