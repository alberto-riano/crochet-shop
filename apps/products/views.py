from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def shop(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    selected_category = request.GET.get('category')

    if selected_category:
        products = products.filter(category__slug=selected_category)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'products/shop.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = product.get_related_products()

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)
