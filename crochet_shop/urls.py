from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from pathlib import Path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('apps.products.urls')),
    path('cart/', include('apps.orders.urls')),
    path('accounts/', include('apps.accounts.urls')),
    # Standalone landing pages
    path('fsc/', serve, {
        'document_root': Path(settings.BASE_DIR) / 'fsc',
        'path': 'index.html',
    }),
    path('fsc/<path:path>', serve, {
        'document_root': Path(settings.BASE_DIR) / 'fsc',
    }),
    path('', include('apps.pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
