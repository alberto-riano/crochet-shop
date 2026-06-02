from django import forms

from .models import Product


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class ProductAdminForm(forms.ModelForm):
    gallery_images = forms.FileField(
        required=False,
        widget=MultipleFileInput(),
        label="Imágenes de galería",
        help_text="Puedes seleccionar varias imágenes y se añadirán a la galería del producto.",
    )

    class Meta:
        model = Product
        fields = "__all__"
