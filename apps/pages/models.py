from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre')
    email = models.EmailField(verbose_name='Email')
    message = models.TextField(verbose_name='Mensaje')
    is_read = models.BooleanField(default=False, verbose_name='Leído')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y')}"


class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=100, default='Miles de Puntos', verbose_name='Nombre del sitio')
    tagline = models.CharField(
        max_length=200, default='Hecho a mano, punto a punto',
        verbose_name='Eslogan'
    )
    about_text = models.TextField(blank=True, verbose_name='Texto "Sobre nosotras"')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')
    facebook_url = models.URLField(blank=True, verbose_name='Facebook')
    pinterest_url = models.URLField(blank=True, verbose_name='Pinterest')
    email = models.EmailField(default='milesdepuntos@gmail.com', verbose_name='Email de contacto')

    class Meta:
        verbose_name = 'Configuración del sitio'
        verbose_name_plural = 'Configuración del sitio'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Singleton pattern - only one config
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config
