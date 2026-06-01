# 🧶 Lazadas — Crochet by Paula

Tienda online artesanal de productos de crochet hechos a mano por Paula Miles Uribe.

## Descripción

Lazadas es una aplicación web desarrollada con Django que permite vender productos de crochet artesanales en dos modalidades:
- **Encargo personalizado**: piezas terminadas con opciones de personalización
- **Pack DIY**: materiales + patrón PDF + código QR con acceso a vídeo tutorial

## Requisitos previos

- Python 3.10+
- pip

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate  # macOS/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Cargar datos de ejemplo
python manage.py seed_data

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Ejecutar servidor
python manage.py runserver
```

## Acceso

- **Tienda**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## Estructura del proyecto

```
crochet_shop/
├── manage.py
├── requirements.txt
├── crochet_shop/          # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── products/          # Productos y categorías
│   ├── orders/            # Carrito y pedidos
│   ├── accounts/          # Usuarios
│   └── pages/             # Home, about, contacto
├── templates/             # Templates HTML
├── static/                # CSS, JS, imágenes
└── media/                 # Archivos subidos
```

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| SECRET_KEY | Clave secreta Django | - |
| DEBUG | Modo debug | True |
| ALLOWED_HOSTS | Hosts permitidos | 127.0.0.1,localhost |

## Rutas principales

| URL | Descripción |
|-----|-------------|
| `/` | Página de inicio |
| `/shop/` | Tienda con todos los productos |
| `/shop/<slug>/` | Detalle de producto |
| `/cart/` | Carrito de compra |
| `/cart/checkout/` | Finalizar pedido |
| `/about/` | Sobre nosotros |
| `/contact/` | Contacto |
| `/admin/` | Panel de administración |

## Tecnologías

- Django 4.2+
- Bootstrap 5
- django-jazzmin (admin)
- django-crispy-forms
- WhiteNoise (estáticos)
- qrcode (generación QR)
- Pillow (imágenes)

## Créditos

- **Artesana**: Paula Miles Uribe
- **Desarrollo web**: Alberto Riaño González
