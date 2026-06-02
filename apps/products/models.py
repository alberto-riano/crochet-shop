import io
import os
import re
import unicodedata

import qrcode
from django.db import models
from django.db.models import Max
from django.core.files.base import ContentFile
from django.utils.text import slugify


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
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

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
        upload_to='products/covers/', verbose_name='Imagen principal'
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name='Precio (€)'
    )
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2,
        blank=True, null=True,
        verbose_name='Precio rebajado (€)',
        help_text='Dejar vacío si no está en oferta'
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
        upload_to='products/qr/', blank=True,
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
        if self.cover_image and not self.cover_image._committed:
            ext = _normalized_extension(self.cover_image.name)
            self.cover_image.name = self._build_cover_filename(ext)
        if self.video_url and not self.qr_code:
            self._generate_qr()
        super().save(*args, **kwargs)

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

    def _build_base_photo_name(self):
        category_token = _category_label(self.category)
        product_token = _normalize_token(self.name)
        return f'{self.product_id}_{category_token}_{product_token}'

    def _build_cover_filename(self, ext):
        base_name = self._build_base_photo_name()
        return f'products/covers/{base_name}_01{ext}'

    def build_gallery_filename(self, sequence_number, ext):
        base_name = self._build_base_photo_name()
        return f'products/gallery/{base_name}_{sequence_number:02d}{ext}'

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
        upload_to='products/gallery/', verbose_name='Imagen'
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

        if self.image and not self.image._committed:
            ext = _normalized_extension(self.image.name)
            self.image.name = self.product.build_gallery_filename(self.order, ext)

        super().save(*args, **kwargs)
