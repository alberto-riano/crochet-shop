from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Product, ProductImage


@receiver(post_delete, sender=ProductImage)
def delete_product_image_from_s3(sender, instance, **kwargs):
    """Delete the image file from S3 when a ProductImage is deleted."""
    if instance.image:
        instance.image.delete(save=False)


@receiver(post_delete, sender=Product)
def delete_product_files_from_s3(sender, instance, **kwargs):
    """Delete cover and QR from S3 when a Product is deleted."""
    if instance.cover_image:
        instance.cover_image.delete(save=False)
    if instance.qr_code:
        instance.qr_code.delete(save=False)


@receiver(pre_save, sender=Product)
def delete_old_cover_on_change(sender, instance, **kwargs):
    """If cover_image is replaced, delete the old one from S3."""
    if not instance.pk:
        return
    try:
        old = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return
    if old.cover_image and old.cover_image != instance.cover_image:
        old.cover_image.delete(save=False)


@receiver(pre_save, sender=ProductImage)
def delete_old_gallery_image_on_change(sender, instance, **kwargs):
    """If a gallery image file is replaced, delete the old one from S3."""
    if not instance.pk:
        return
    try:
        old = ProductImage.objects.get(pk=instance.pk)
    except ProductImage.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        old.image.delete(save=False)
