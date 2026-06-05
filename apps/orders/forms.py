from django import forms


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ('bizum', 'Bizum'),
        ('transfer', 'Transferencia bancaria'),
    ]

    customer_name = forms.CharField(
        max_length=200, label='Nombre completo',
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre completo'})
    )
    customer_email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'tu@email.com'})
    )
    customer_phone = forms.CharField(
        max_length=20, label='Teléfono',
        widget=forms.TextInput(attrs={'placeholder': '+34 600 000 000'})
    )
    customer_address = forms.CharField(
        label='Dirección de envío',
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Calle, número, piso, código postal, ciudad'})
    )
    notes = forms.CharField(
        required=False, label='Notas adicionales',
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Algún detalle extra sobre tu pedido...'})
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES, label='Método de pago',
        widget=forms.HiddenInput,  # Managed by custom UI in template
    )
