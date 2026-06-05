import uuid
from django.db import models
from apps.products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('in_production', 'En producción'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('bizum', 'Bizum'),
        ('transfer', 'Transferencia bancaria'),
        ('card', 'Tarjeta de crédito'),
    ]

    reference = models.CharField(
        max_length=12, unique=True, verbose_name='Referencia'
    )
    customer_name = models.CharField(max_length=200, verbose_name='Nombre completo')
    customer_email = models.EmailField(verbose_name='Email')
    customer_phone = models.CharField(max_length=20, verbose_name='Teléfono')
    customer_address = models.TextField(verbose_name='Dirección de envío')
    notes = models.TextField(blank=True, verbose_name='Notas adicionales')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
        verbose_name='Estado'
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True,
        verbose_name='Método de pago'
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='Total (€)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.reference} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    ORDER_TYPE_CHOICES = [
        ('custom_order', 'Encargo personalizado'),
        ('kit', 'Pack DIY'),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name='Pedido'
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True,
        verbose_name='Producto'
    )
    product_name = models.CharField(max_length=200, verbose_name='Nombre producto')
    order_type = models.CharField(
        max_length=20, choices=ORDER_TYPE_CHOICES,
        verbose_name='Tipo de pedido'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    unit_price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name='Precio unitario'
    )
    customization_notes = models.TextField(
        blank=True, verbose_name='Notas de personalización'
    )
    chosen_color = models.CharField(
        max_length=100, blank=True, verbose_name='Color elegido'
    )

    class Meta:
        verbose_name = 'Artículo del pedido'
        verbose_name_plural = 'Artículos del pedido'

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
