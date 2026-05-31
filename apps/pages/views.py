from django.shortcuts import render, redirect
from django.contrib import messages
from apps.products.models import Product
from .models import ContactMessage, SiteConfiguration
from .forms import ContactForm


def home(request):
    latest_products = Product.objects.filter(is_available=True)[:4]
    config = SiteConfiguration.get_config()
    context = {
        'latest_products': latest_products,
        'config': config,
    }
    return render(request, 'pages/home.html', context)


def about(request):
    config = SiteConfiguration.get_config()
    return render(request, 'pages/about.html', {'config': config})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message'],
            )
            messages.success(request, '¡Mensaje enviado! Te responderemos en 24-48 horas.')
            return redirect('pages:contact')
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form})
