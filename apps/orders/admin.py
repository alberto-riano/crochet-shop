from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'order_type', 'quantity', 'unit_price', 'customization_notes', 'chosen_color']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'customer_name', 'customer_email', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['reference', 'customer_name', 'customer_email']
    readonly_fields = ['reference', 'created_at']
    inlines = [OrderItemInline]
    list_editable = ['status']
