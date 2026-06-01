import os
import re
import shutil
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from apps.products.models import Category, Product, ProductImage


CATEGORIES = {
    '01': {'name': 'Amigurumis', 'slug': 'amigurumis', 'description': 'Muñecos y figuras tejidas a ganchillo con todo el cariño'},
    '02': {'name': 'Complementos', 'slug': 'complementos', 'description': 'Bolsos, bolsas y complementos tejidos a mano'},
    '03': {'name': 'Ropa', 'slug': 'ropa', 'description': 'Prendas de ropa tejidas a mano con materiales de calidad'},
}

# Pattern: CCPPPP_Category_Name_NN.ext
PHOTO_PATTERN = re.compile(
    r'^(\d{2})(\d{4})_([^_]+)_(.+?)_(\d{2})\.(jpg|jpeg|png|heic)$',
    re.IGNORECASE
)


class Command(BaseCommand):
    help = 'Carga los productos reales desde la carpeta photos/ usando el formato de nombre'

    def handle(self, *args, **options):
        Product.objects.all().delete()
        ProductImage.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write('Base de datos limpia.')

        # Create categories
        cat_objects = {}
        for code, data in CATEGORIES.items():
            cat_objects[code] = Category.objects.create(
                name=data['name'],
                slug=data['slug'],
                code=code,
                description=data['description'],
            )
        self.stdout.write(self.style.SUCCESS(f'Creadas {len(cat_objects)} categorías.'))

        # Scan photos folder
        photos_dir = settings.BASE_DIR / 'photos'
        media_covers = settings.MEDIA_ROOT / 'products' / 'covers'
        media_gallery = settings.MEDIA_ROOT / 'products' / 'gallery'
        media_covers.mkdir(parents=True, exist_ok=True)
        media_gallery.mkdir(parents=True, exist_ok=True)

        # Group photos by product_id
        products_photos = defaultdict(list)
        for filename in sorted(os.listdir(photos_dir)):
            match = PHOTO_PATTERN.match(filename)
            if match:
                cat_code = match.group(1)
                prod_num = match.group(2)
                product_id = f'{cat_code}{prod_num:>04}'
                # Full 8-digit ID
                full_id = f'{cat_code}{int(prod_num):06d}'
                name_parts = match.group(4).replace('_', ' ')
                category_name = match.group(3)
                seq = int(match.group(5))
                products_photos[full_id].append({
                    'filename': filename,
                    'name': name_parts,
                    'category_code': cat_code,
                    'seq': seq,
                })

        # Create products
        for product_id, photos in sorted(products_photos.items()):
            photos.sort(key=lambda x: x['seq'])
            first = photos[0]
            cat_code = first['category_code']
            product_name = first['name']

            # Cover = first photo (_01)
            cover_file = first['filename']
            cover_src = photos_dir / cover_file
            cover_dest = media_covers / cover_file
            shutil.copy2(str(cover_src), str(cover_dest))

            product = Product.objects.create(
                product_id=product_id,
                name=product_name,
                slug=slugify(product_name) or slugify(f'{product_name}-{product_id}'),
                description=f'{product_name} hecho a mano por Paula. Pieza única tejida con materiales de calidad.',
                category=cat_objects[cat_code],
                cover_image=f'products/covers/{cover_file}',
                price=0,  # To be set from admin
                is_customizable=True,
                is_available=True,
            )

            # Additional photos as gallery
            for photo in photos[1:]:
                gallery_src = photos_dir / photo['filename']
                gallery_dest = media_gallery / photo['filename']
                shutil.copy2(str(gallery_src), str(gallery_dest))
                ProductImage.objects.create(
                    product=product,
                    image=f"products/gallery/{photo['filename']}",
                    alt_text=f"{product_name} - foto {photo['seq']}",
                    order=photo['seq'],
                )

            photo_count = len(photos)
            self.stdout.write(f"  ✓ [{product_id}] {product_name} ({photo_count} foto{'s' if photo_count > 1 else ''})")

        total = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n¡Catálogo cargado! {total} productos. Fija los precios desde el admin.'))
