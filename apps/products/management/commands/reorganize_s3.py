"""
Management command to reorganize existing S3 media files from the old flat
structure to the new product_id-based structure.

Old structure:
  media/products/covers/{product_id}_{Category}_{Name}_01.jpg
  media/products/gallery/{product_id}_{Category}_{Name}_NN.jpg
  media/products/qr/qr_{slug}.png
  media/categories/{filename}

New structure (under {S3_ENV}/ prefix):
  products/{product_id}/cover/{name}.jpg
  products/{product_id}/gallery/{NN}.jpg
  products/{product_id}/qr/qr.png
  categories/{slug}.jpg

Usage:
  python manage.py reorganize_s3 --dry-run   # Preview changes
  python manage.py reorganize_s3             # Execute
"""
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.products.models import (
    Category, Product, ProductImage,
    _normalize_token, _normalized_extension,
)


class Command(BaseCommand):
    help = 'Reorganize existing S3 files to the new product_id-based structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be moved without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        env_prefix = settings.S3_ENV

        moves = []
        db_updates = []

        # --- Products ---
        for product in Product.objects.select_related('category').all():
            # Cover image → products/{product_id}/{product_id}_01.ext
            if product.cover_image:
                old_key = f'{env_prefix}/{product.cover_image.name}'
                ext = _normalized_extension(product.cover_image.name)
                new_relative = f'products/{product.product_id}/{product.product_id}_01{ext}'
                new_key = f'{env_prefix}/{new_relative}'

                if old_key != new_key:
                    moves.append((old_key, new_key))
                    db_updates.append(('product_cover', product.pk, new_relative))

            # QR code → products/{product_id}/{product_id}_qr.png
            if product.qr_code:
                old_key = f'{env_prefix}/{product.qr_code.name}'
                new_relative = f'products/{product.product_id}/{product.product_id}_qr.png'
                new_key = f'{env_prefix}/{new_relative}'

                if old_key != new_key:
                    moves.append((old_key, new_key))
                    db_updates.append(('product_qr', product.pk, new_relative))

        # --- Gallery images → products/{product_id}/{product_id}_{seq}.ext ---
        for img in ProductImage.objects.select_related('product').all():
            if img.image:
                old_key = f'{env_prefix}/{img.image.name}'
                ext = _normalized_extension(img.image.name)
                seq = img.order if img.order > 0 else 1
                pid = img.product.product_id
                new_relative = f'products/{pid}/{pid}_{seq:02d}{ext}'
                new_key = f'{env_prefix}/{new_relative}'

                if old_key != new_key:
                    moves.append((old_key, new_key))
                    db_updates.append(('gallery', img.pk, new_relative))

        # --- Categories ---
        for cat in Category.objects.all():
            if cat.image:
                old_key = f'{env_prefix}/{cat.image.name}'
                ext = _normalized_extension(cat.image.name)
                new_relative = f'categories/{cat.slug}{ext}'
                new_key = f'{env_prefix}/{new_relative}'

                if old_key != new_key:
                    moves.append((old_key, new_key))
                    db_updates.append(('category', cat.pk, new_relative))

        if not moves:
            self.stdout.write(self.style.SUCCESS('Nothing to move — all files already in the correct structure.'))
            return

        self.stdout.write(f'\n{"[DRY RUN] " if dry_run else ""}Moving {len(moves)} files:\n')

        for old_key, new_key in moves:
            self.stdout.write(f'  {old_key}\n    → {new_key}')

            if not dry_run:
                # Copy to new location
                try:
                    s3.copy_object(
                        Bucket=bucket,
                        CopySource={'Bucket': bucket, 'Key': old_key},
                        Key=new_key,
                    )
                    # Delete old file
                    s3.delete_object(Bucket=bucket, Key=old_key)
                except s3.exceptions.NoSuchKey:
                    self.stdout.write(self.style.WARNING(f'    ⚠ Source not found, skipping'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ✗ Error: {e}'))
                    continue

        if not dry_run:
            # Update database references
            self.stdout.write('\nUpdating database references...')
            for update_type, pk, new_path in db_updates:
                if update_type == 'product_cover':
                    Product.objects.filter(pk=pk).update(cover_image=new_path)
                elif update_type == 'product_qr':
                    Product.objects.filter(pk=pk).update(qr_code=new_path)
                elif update_type == 'gallery':
                    ProductImage.objects.filter(pk=pk).update(image=new_path)
                elif update_type == 'category':
                    Category.objects.filter(pk=pk).update(image=new_path)

            self.stdout.write(self.style.SUCCESS(f'\n✓ Done! {len(moves)} files reorganized.'))
        else:
            self.stdout.write(self.style.WARNING(f'\n[DRY RUN] No changes made. Run without --dry-run to execute.'))
