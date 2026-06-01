from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'category', 'price', 'discount_price', 'is_on_sale', 'is_available']
    list_filter = ['category', 'is_available', 'is_customizable']
    search_fields = ['name', 'description', 'product_id']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ['price', 'discount_price', 'is_available']
    readonly_fields = ['product_id']
    fieldsets = (
        (None, {
            'fields': ('product_id', 'name', 'slug', 'category', 'description', 'cover_image')
        }),
        ('Precios', {
            'fields': ('price', 'discount_price'),
            'description': 'El precio rebajado aparecerá como oferta en la web (precio original tachado).'
        }),
        ('Personalización', {
            'fields': ('is_customizable', 'customization_options')
        }),
        ('Extras', {
            'fields': ('video_url', 'qr_code', 'is_available')
        }),
    )
