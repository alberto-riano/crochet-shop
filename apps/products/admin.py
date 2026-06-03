from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from .models import Category, Product, ProductImage
from .forms import ProductAdminForm


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    can_delete = True  # Allows deleting images (signal handles S3 cleanup)
    readonly_fields = ['image_preview', 's3_path']
    fields = ['image_preview', 's3_path', 'image', 'alt_text', 'order']

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="height:48px;width:48px;object-fit:cover;border-radius:6px;"/>',
                obj.image.url,
                obj.alt_text or 'preview'
            )
        return '-'

    image_preview.short_description = 'Vista'

    def s3_path(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<code style="font-size:11px;color:#666;">{}</code>',
                obj.image.name
            )
        return '-'

    s3_path.short_description = 'Ruta en S3'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = [
        'product_id', 'name', 'category', 'price', 'diy_price',
        'stock', 'is_available', 'is_diy_available', 'is_customizable'
    ]
    list_filter = ['category', 'is_available', 'is_diy_available', 'is_customizable']
    search_fields = ['name', 'description', 'product_id']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ['price', 'diy_price', 'stock', 'is_available', 'is_diy_available']
    readonly_fields = ['product_id', 'cover_s3_path']
    fieldsets = (
        (None, {
            'fields': ('product_id', 'name', 'slug', 'category', 'description', 'cover_image', 'cover_s3_path')
        }),
        ('Precios y disponibilidad', {
            'fields': ('price', 'discount_price', 'stock', 'is_available'),
            'description': 'Precio de la pieza terminada. El rebajado aparecerá como oferta (precio original tachado).'
        }),
        ('Pack DIY', {
            'fields': ('is_diy_available', 'diy_price'),
            'description': 'Activa si este producto se puede comprar como kit: materiales + patrón PDF + vídeo tutorial.'
        }),
        ('Personalización', {
            'fields': ('is_customizable', 'customization_options')
        }),
        ('Extras', {
            'fields': ('video_url', 'qr_code', 'gallery_images')
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        gallery_images = request.FILES.getlist('gallery_images')
        if not gallery_images:
            return

        # Start after the highest existing order (cover is always order=1)
        last_order = form.instance.images.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 1
        for idx, image in enumerate(gallery_images, start=1):
            ProductImage.objects.create(
                product=form.instance,
                image=image,
                alt_text=f'{form.instance.name} - imagen {last_order + idx}',
                order=last_order + idx,
            )

    def cover_s3_path(self, obj):
        if obj and obj.cover_image:
            return format_html(
                '<code style="font-size:11px;color:#666;">{}</code>',
                obj.cover_image.name
            )
        return '-'

    cover_s3_path.short_description = 'Portada en S3'
