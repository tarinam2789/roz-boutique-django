from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    tagline = models.CharField(max_length=200, blank=True, null=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.name


class Product(models.Model):
    BOTTOM_TYPE_CHOICES = [
        ("Shalwar", "Shalwar"),
        ("Trouser", "Trouser"),
        ("Skirt", "Skirt"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    fabric = models.CharField(max_length=200, blank=True, null=True)
    swatch = models.IntegerField(default=0)
    image_path = models.FileField(upload_to="uploads/", blank=True, null=True)
    bottom_type = models.CharField(max_length=20, choices=BOTTOM_TYPE_CHOICES, blank=True, null=True)
    is_best_seller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    season = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")
    color_name = models.CharField(max_length=100)
    hex = models.CharField(max_length=7)

    class Meta:
        unique_together = ("product", "color_name")

    def __str__(self):
        return f"{self.product.name} — {self.color_name}"


class ProductMedia(models.Model):
    MEDIA_TYPE_CHOICES = [("image", "Image"), ("video", "Video")]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default="image")
    path = models.FileField(upload_to="uploads/")
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class ProductSize(models.Model):
    SIZE_CHOICES = [
        ("XS", "XS"), ("S", "S"), ("M", "M"),
        ("L", "L"), ("XL", "XL"), ("XXL", "XXL"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size_code = models.CharField(max_length=5, choices=SIZE_CHOICES)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ("product", "size_code")


class SizeGuide(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="size_guide")
    instructions = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=5, default="in")


class SizeGuideRow(models.Model):
    SIZE_CHOICES = [
        ("XS", "XS"), ("S", "S"), ("M", "M"),
        ("L", "L"), ("XL", "XL"), ("XXL", "XXL"),
    ]

    size_guide = models.ForeignKey(SizeGuide, on_delete=models.CASCADE, related_name="rows")
    size_code = models.CharField(max_length=5, choices=SIZE_CHOICES)
    chest = models.FloatField("Chest", blank=True, null=True)
    waist = models.FloatField("Waist", blank=True, null=True)
    length = models.FloatField("Dress Length", blank=True, null=True)
    sleeve_length = models.FloatField("Sleeve Length", blank=True, null=True)
    bottom_length = models.FloatField("Trouser Length", blank=True, null=True)



class ShippingRule(models.Model):
    country = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=10, default="USD")
    standard_price = models.DecimalField(max_digits=10, decimal_places=2)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=100)

    def __str__(self):
        return self.country


class ReturnPolicy(models.Model):
    window_days = models.IntegerField(default=14)
    return_fee = models.DecimalField(max_digits=10, decimal_places=2, default=12)
    eligibility_rules = models.TextField(blank=True, null=True)
    refund_method = models.TextField(blank=True, null=True)


class Order(models.Model):
    STATUS_CHOICES = [("Placed", "Placed"), ("Shipped", "Shipped"), ("Delivered", "Delivered")]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Placed")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    country = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    size_code = models.CharField(max_length=5)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class ReturnRequest(models.Model):
    STATUS_CHOICES = [("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")]

    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="return_requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    admin_note = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InstagramPost(models.Model):
    caption = models.CharField(max_length=300, blank=True, null=True)
    swatch = models.IntegerField(default=0)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
