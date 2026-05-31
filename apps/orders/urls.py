from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<str:cart_key>/', views.remove_from_cart, name='remove'),
    path('update/<str:cart_key>/', views.update_cart, name='update'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<str:reference>/', views.order_confirmation, name='confirmation'),
]
