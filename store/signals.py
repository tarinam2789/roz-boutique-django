from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductMedia


@receiver([post_save, post_delete], sender=ProductMedia)
def sync_product_cover_image(sender, instance, **kwargs):
    """Keeps Product.image_path (the cover shown on listing cards) in sync
    with the first photo in the product's gallery — added or removed."""
    product = instance.product
    first_image = (
        ProductMedia.objects
        .filter(product=product, media_type="image")
        .order_by("sort_order", "id")
        .first()
    )
    if first_image:
        product.image_path.name = first_image.path.name
    else:
        product.image_path = None
    product.save(update_fields=["image_path"])
