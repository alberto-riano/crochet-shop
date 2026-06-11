import io
import os
import re
import unicodedata

import qrcode
from PIL import Image as PILImage
from django.db import models
from django.db.models import Max
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify


# --------------- Image optimization ---------------
MAX_IMAGE_WIDTH = 1200  # px — sufficient for detail view
THUMBNAIL_WIDTH = 600   # px — for product cards
JPEG_QUALITY = 75


def _compress_image(image_field, max_width=MAX_IMAGE_WIDTH, quality=JPEG_QUALITY):
    """Compress and resize an ImageField in-place before saving to storage."""
    if not image_field:
        return
    try:
        img = PILImage.open(image_field)
    except Exception:
        return

    # Convert RGBA/P to RGB for JPEG
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Resize if wider than max_width, keeping aspect ratio
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), PILImage.LANCZOS)

    # Save as optimized JPEG
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)

    # Replace field file content
    name = os.path.splitext(image_field.name)[0] + '.jpg'
    image_field.save(
        name,
        ContentFile(buffer.read()),
        save=False,
    )


def _normalize_token(value):
    normalized = unicodedata.normalize('NFKD', value or '')
    normalized = normalized.encode('ascii', 'ignore').decode('ascii')
    normalized = re.sub(r'[^A-Za-z0-9]+', '_', normalized)
    normalized = re.sub(r'_+', '_', normalized).strip('_')
    return normalized or 'SinNombre'


def _normalized_extension(filename):
    ext = os.path.splitext(filename or '')[1].lower()
    return ext if ext else '.jpg'


def _category_label(category):
    raw = category.name if category else 'Categoria'
    normalized = _normalize_token(raw)
    mapping = {
        'Amigurumis': 'Amigurumi',
        'Complementos': 'Complemento',
        'Ropa': 'Ropa',
    }
    return mapping.get(normalized, normalized)


def _product_cover_path(instance, filename):
    """Upload cover to: products/{product_id}/{product_id}_01.{ext}"""
    ext = _normalized_extension(filename)
    return f'products/{instance.product_id}/{instance.product_id}_01{ext}'


def _product_qr_path(instance, filename):
    """Upload QR to: products/{product_id}/{product_id}_qr.png"""
    return f'products/{instance.product_id}/{instance.product_id}_qr.png'


def _product_gallery_path(instance, filename):
    """Upload gallery image to: products/{product_id}/{product_id}_{seq}.{ext}"""
    ext = _normalized_extension(filename)
    seq = instance.order if instance.order > 0 else 1
    return f'products/{instance.product.product_id}/{instance.product.product_id}_{seq:02d}{ext}'


def _category_image_path(instance, filename):
    """Upload category image to: categories/{slug}.{ext}"""
    ext = _normalized_extension(filename)
    return f'categories/{instance.slug}{ext}'


class Category(models.Model):
    CATEGORY_CODES = {
        'amigurumis': '01',
        'complementos': '02',
        'ropa': '03',
    }

    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    code = models.CharField(
        max_length=2, unique=True, verbose_name='Código (2 dígitos)',
        help_text='Código numérico de 2 dígitos para el ID del producto'
    )
    description = models.TextField(blank=True, verbose_name='Descripción')
    image = models.ImageField(upload_to=_category_image_path, blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['code']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    product_id = models.CharField(
        max_length=8, unique=True, verbose_name='ID Producto',
        help_text='Formato: 2 dígitos categoría + 6 dígitos producto (ej: 01000001)'
    )
    name = models.CharField(max_length=200, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Descripción')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='products', verbose_name='Categoría'
    )
    cover_image = models.ImageField(
        upload_to=_product_cover_path, verbose_name='Imagen principal'
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name='Precio pieza (€)'
    )
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2,
        blank=True, null=True,
        verbose_name='Precio rebajado (€)',
        help_text='Dejar vacío si no está en oferta'
    )
    diy_price = models.DecimalField(
        max_digits=8, decimal_places=2,
        blank=True, null=True,
        verbose_name='Precio DIY (€)',
        help_text='Si tiene valor, el producto se ofrece como Pack DIY en la web'
    )
    is_customizable = models.BooleanField(
        default=True, verbose_name='¿Personalizable?'
    )
    customization_options = models.TextField(
        blank=True,
        verbose_name='Opciones de personalización',
        help_text='Colores disponibles, separados por coma'
    )
    video_url = models.URLField(
        blank=True, verbose_name='URL del vídeo tutorial'
    )
    qr_code = models.ImageField(
        upload_to=_product_qr_path, blank=True,
        verbose_name='Código QR'
    )
    is_available = models.BooleanField(
        default=True, verbose_name='Disponible'
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Stock',
        help_text='Unidades disponibles para vender'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['product_id']

    def __str__(self):
        return f'[{self.product_id}] {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.product_id and self.category:
            self.product_id = self._generate_product_id()
        if self.video_url and not self.qr_code:
            self._generate_qr()
        # Compress cover image if it's a new upload
        if self.cover_image and hasattr(self.cover_image.file, 'read'):
            _compress_image(self.cover_image, max_width=MAX_IMAGE_WIDTH)
        # Track if cover changed to sync gallery later
        self._cover_changed = self.cover_image and (
            not self.pk or self._cover_image_changed()
        )
        super().save(*args, **kwargs)
        # Sync cover as first gallery image (order=1)
        if self._cover_changed:
            self._sync_cover_to_gallery()

    def _cover_image_changed(self):
        try:
            old = Product.objects.get(pk=self.pk)
            return old.cover_image != self.cover_image
        except Product.DoesNotExist:
            return True

    def _sync_cover_to_gallery(self):
        """Ensure cover image exists as ProductImage with order=1."""
        cover_entry = self.images.filter(order=1).first()
        if cover_entry:
            # Update existing order=1 entry to point to same file
            if cover_entry.image.name != self.cover_image.name:
                cover_entry.image = self.cover_image
                cover_entry.alt_text = f'{self.name} - portada'
                ProductImage.objects.filter(pk=cover_entry.pk).update(
                    image=self.cover_image.name,
                    alt_text=f'{self.name} - portada',
                )
        else:
            # Create new gallery entry for the cover
            ProductImage.objects.create(
                product=self,
                image=self.cover_image.name,
                alt_text=f'{self.name} - portada',
                order=1,
            )

    def _generate_product_id(self):
        last = Product.objects.filter(
            product_id__startswith=self.category.code
        ).order_by('-product_id').first()
        if last:
            seq = int(last.product_id[2:]) + 1
        else:
            seq = 1
        return f'{self.category.code}{seq:06d}'

    def _generate_qr(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(self.video_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#5C4033", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.slug}.png'
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    @property
    def display_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def is_on_sale(self):
        return self.discount_price is not None

    @property
    def colors_list(self):
        if self.customization_options:
            return [c.strip() for c in self.customization_options.split(',')]
        return []

    def get_related_products(self):
        return Product.objects.filter(
            category=self.category, is_available=True
        ).exclude(pk=self.pk)[:4]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='images', verbose_name='Producto'
    )
    image = models.ImageField(
        upload_to=_product_gallery_path, verbose_name='Imagen'
    )
    alt_text = models.CharField(
        max_length=200, blank=True, verbose_name='Texto alternativo'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')

    class Meta:
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de producto'
        ordering = ['order']

    def __str__(self):
        return f"Imagen de {self.product.name}"

    def save(self, *args, **kwargs):
        if self.order <= 0:
            max_order = ProductImage.objects.filter(product=self.product).aggregate(
                max_order=Max('order')
            )['max_order'] or 0
            self.order = max_order + 1

        # Compress gallery image if it's a new upload
        if self.image and hasattr(self.image.file, 'read'):
            _compress_image(self.image, max_width=MAX_IMAGE_WIDTH)

        super().save(*args, **kwargs)
