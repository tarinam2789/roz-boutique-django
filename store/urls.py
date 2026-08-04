from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("category/<slug:slug>", views.category_page, name="category_page"),
    path("product/<slug:slug>", views.product_detail, name="product_detail"),

    path("wishlist/toggle", views.wishlist_toggle, name="wishlist_toggle"),
    path("wishlist", views.wishlist_page, name="wishlist_page"),
    path("search", views.search, name="search"),

    path("cart/add", views.cart_add, name="cart_add"),
    path("cart", views.cart_page, name="cart_page"),
    path("cart/update", views.cart_update, name="cart_update"),
    path("cart/remove", views.cart_remove, name="cart_remove"),

    path("checkout", views.checkout, name="checkout"),
    path("order/confirmation/<int:order_id>", views.order_confirmation, name="order_confirmation"),
    path("newsletter/subscribe", views.newsletter_subscribe, name="newsletter_subscribe"),

    path("account/register", views.account_register, name="account_register"),
    path("account/login", views.account_login, name="account_login"),
    path("account/logout", views.account_logout, name="account_logout"),
    path("account/dashboard", views.account_dashboard, name="account_dashboard"),
    path("account/return-request", views.account_return_request, name="account_return_request"),

    path("policies", views.policies, name="policies"),
    path("contact", views.contact, name="contact"),
]
