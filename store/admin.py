from django.contrib import admin
from .models import (
    Category, Product, ProductColor, ProductMedia, ProductSize,
    SizeGuide, SizeGuideRow,
    ShippingRule, ReturnPolicy, Order, OrderItem, ReturnRequest,
    ContactMessage, Review, NewsletterSubscriber, InstagramPost,
)

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


def prefilled_formset(base_formset):
    class PrefilledFormset(base_formset):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            has_rows = self.instance.pk and self.queryset.exists()
            if not has_rows:
                for i, form in enumerate(self.forms):
                    if i < len(SIZE_ORDER):
                        form.initial["size_code"] = SIZE_ORDER[i]
    return PrefilledFormset


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 3
    fields = ("media_type", "path", "sort_order")


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 6


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 2


class SizeGuideInline(admin.StackedInline):
    model = SizeGuide
    max_num = 1
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "bottom_type", "active")
    inlines = [ProductMediaInline, ProductSizeInline, ProductColorInline, SizeGuideInline]


class SizeGuideRowInline(admin.TabularInline):
    model = SizeGuideRow
    extra = 6
    max_num = 6
    fields = ("size_code", "chest", "waist", "length", "sleeve_length", "bottom_length")
    get_formset = lambda self, request, obj=None, **kw: prefilled_formset(super(SizeGuideRowInline, self).get_formset(request, obj, **kw))


@admin.register(SizeGuide)
class SizeGuideAdmin(admin.ModelAdmin):
    list_display = ("product", "unit")
    inlines = [SizeGuideRowInline]


admin.site.register(Category)
admin.site.register(ShippingRule)
admin.site.register(ReturnPolicy)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ReturnRequest)
admin.site.register(ContactMessage)
admin.site.register(Review)
admin.site.register(NewsletterSubscriber)
admin.site.register(InstagramPost)
