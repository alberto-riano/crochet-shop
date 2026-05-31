from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.products.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm


def _get_cart(request):
    """Get cart from session."""
    return request.session.get('cart', {})


def _save_cart(request, cart):
    """Save cart to session."""
    request.session['cart'] = cart
    request.session.modified = True


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_available=True)
        order_type = request.POST.get('order_type', 'custom_order')
        color = request.POST.get('color', '')
        custom_notes = request.POST.get('custom_notes', '')

        cart = _get_cart(request)
        cart_key = f"{product_id}_{order_type}_{color}"

        if cart_key in cart:
            cart[cart_key]['quantity'] += 1
        else:
            price = float(product.price_custom_order if order_type == 'custom_order' else product.price_kit)
            cart[cart_key] = {
                'product_id': product_id,
                'name': product.name,
                'order_type': order_type,
                'order_type_display': 'Encargo personalizado' if order_type == 'custom_order' else 'Pack DIY',
                'quantity': 1,
                'price': price,
                'color': color,
                'custom_notes': custom_notes,
                'image_url': product.cover_image.url if product.cover_image else '',
            }

        _save_cart(request, cart)
        messages.success(request, f'"{product.name}" añadido al carrito.')
    return redirect('orders:cart')


def cart_view(request):
    cart = _get_cart(request)
    cart_items_with_keys = []
    for key, item in cart.items():
        item_copy = dict(item)
        item_copy['cart_key'] = key
        cart_items_with_keys.append(item_copy)
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    context = {
        'cart_items': cart_items_with_keys,
        'total': total,
    }
    return render(request, 'orders/cart.html', context)


def remove_from_cart(request, cart_key):
    cart = _get_cart(request)
    if cart_key in cart:
        del cart[cart_key]
        _save_cart(request, cart)
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('orders:cart')


def update_cart(request, cart_key):
    if request.method == 'POST':
        cart = _get_cart(request)
        if cart_key in cart:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart[cart_key]['quantity'] = quantity
            else:
                del cart[cart_key]
            _save_cart(request, cart)
    return redirect('orders:cart')


def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('orders:cart')

    cart_items = list(cart.values())
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data['customer_email'],
                customer_phone=form.cleaned_data['customer_phone'],
                customer_address=form.cleaned_data['customer_address'],
                notes=form.cleaned_data['notes'],
                payment_method=form.cleaned_data['payment_method'],
                total_price=total,
            )

            for item in cart_items:
                product = Product.objects.filter(id=item['product_id']).first()
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item['name'],
                    order_type=item['order_type'],
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    customization_notes=item.get('custom_notes', ''),
                    chosen_color=item.get('color', ''),
                )

            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True

            return redirect('orders:confirmation', reference=order.reference)
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation(request, reference):
    order = get_object_or_404(Order, reference=reference)
    context = {'order': order}
    return render(request, 'orders/confirmation.html', context)
