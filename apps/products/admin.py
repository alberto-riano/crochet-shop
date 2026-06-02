from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage
from .forms import ProductAdminForm


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview', 's3_key']
    fields = ['image_preview', 's3_key', 'image', 'alt_text', 'order']

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="height:48px;width:48px;object-fit:cover;border-radius:6px;"/>',
                obj.image.url,
                obj.alt_text or 'preview'
            )
        return '-'

    image_preview.short_description = 'Vista'

    def s3_key(self, obj):
        if obj.pk and obj.image:
            return obj.image.name
        return '-'

    s3_key.short_description = 'Archivo en S3'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = [
        'product_id', 'name', 'category', 'price', 'discount_price',
        'stock', 'is_on_sale', 'is_available', 'is_customizable'
    ]
    list_filter = ['category', 'is_available', 'is_customizable']
    search_fields = ['name', 'description', 'product_id']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ['price', 'discount_price', 'stock', 'is_available']
    readonly_fields = ['product_id', 'cover_image_s3_key']
    fieldsets = (
        (None, {
            'fields': ('product_id', 'name', 'slug', 'category', 'description', 'cover_image', 'cover_image_s3_key')
        }),
        ('Precios', {
            'fields': ('price', 'discount_price'),
            'description': 'El precio rebajado aparecerá como oferta en la web (precio original tachado).'
        }),
        ('Stock y disponibilidad', {
            'fields': ('stock', 'is_available')
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

        last_order = form.instance.images.count()
        for idx, image in enumerate(gallery_images, start=1):
            ProductImage.objects.create(
                product=form.instance,
                image=image,
                alt_text=f'{form.instance.name} - imagen {last_order + idx}',
                order=last_order + idx,
            )

    def cover_image_s3_key(self, obj):
        if obj and obj.cover_image:
            return obj.cover_image.name
        return '-'

    cover_image_s3_key.short_description = 'Portada en S3'
