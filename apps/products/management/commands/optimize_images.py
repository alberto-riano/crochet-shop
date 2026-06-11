"""
Management command to optimize all existing product images.
Compresses and resizes images to reduce page load times.

Usage:
    python manage.py optimize_images          # Optimize all product images
    python manage.py optimize_images --dry-run # Preview what would be optimized
"""
import io

from PIL import Image as PILImage
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.products.models import Product, ProductImage, MAX_IMAGE_WIDTH, JPEG_QUALITY


class Command(BaseCommand):
    help = 'Compress and resize all existing product images to optimize load times'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show what would be optimized without making changes',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=MAX_IMAGE_WIDTH,
            help=f'Maximum width in pixels (default: {MAX_IMAGE_WIDTH})',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=JPEG_QUALITY,
            help=f'JPEG quality 1-95 (default: {JPEG_QUALITY})',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        max_width = options['max_width']
        quality = options['quality']

        self.stdout.write(f"Settings: max_width={max_width}px, quality={quality}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be made\n"))

        total_saved = 0

        # Optimize cover images
        products = Product.objects.exclude(cover_image='')
        self.stdout.write(f"\nProcessing {products.count()} product cover images...")
        for product in products:
            saved = self._optimize_field(product, 'cover_image', max_width, quality, dry_run)
            total_saved += saved

        # Optimize gallery images
        gallery_images = ProductImage.objects.exclude(image='')
        self.stdout.write(f"\nProcessing {gallery_images.count()} gallery images...")
        for img in gallery_images:
            saved = self._optimize_field(img, 'image', max_width, quality, dry_run)
            total_saved += saved

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Total space saved: {total_saved / 1024 / 1024:.1f} MB"
        ))

    def _optimize_field(self, instance, field_name, max_width, quality, dry_run):
        image_field = getattr(instance, field_name)
        try:
            image_field.open('rb')
            original_size = image_field.size
            img = PILImage.open(image_field)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Skip {image_field.name}: {e}"))
            return 0

        # Skip small images
        if original_size < 200 * 1024:  # less than 200KB
            return 0

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), PILImage.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        new_size = buffer.tell()
        buffer.seek(0)

        saved_bytes = original_size - new_size
        if saved_bytes <= 0:
            return 0

        pct = (saved_bytes / original_size) * 100
        self.stdout.write(
            f"  {image_field.name}: "
            f"{original_size / 1024:.0f}KB → {new_size / 1024:.0f}KB "
            f"(-{pct:.0f}%)"
        )

        if not dry_run:
            import os
            new_name = os.path.splitext(image_field.name)[0] + '.jpg'
            image_field.save(new_name, ContentFile(buffer.read()), save=False)
            instance.save(update_fields=[field_name])

        return saved_bytes
