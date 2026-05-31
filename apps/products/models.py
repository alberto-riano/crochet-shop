import io
import qrcode
from django.db import models
from django.core.files.base import ContentFile
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Descripción')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
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
    price_custom_order = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name='Precio encargo personalizado (€)'
    )
    price_kit = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name='Precio Pack DIY (€)'
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Generate QR code from video URL
        if self.video_url and not self.qr_code:
            self._generate_qr()
        super().save(*args, **kwargs)

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
    def min_price(self):
        return min(self.price_custom_order, self.price_kit)

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
