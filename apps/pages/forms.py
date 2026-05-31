from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=200, label='Tu nombre',
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'})
    )
    email = forms.EmailField(
        label='Tu email',
        widget=forms.EmailInput(attrs={'placeholder': 'tu@email.com'})
    )
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': '¿En qué podemos ayudarte?'})
    )
