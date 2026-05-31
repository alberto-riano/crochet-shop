from django.core.management.base import BaseCommand
from apps.products.models import Category, Product
from apps.pages.models import SiteConfiguration


class Command(BaseCommand):
    help = 'Carga datos de ejemplo para la tienda Lazadas'

    def handle(self, *args, **options):
        self.stdout.write('Creando categorías...')
        categories = {
            'amigurumis': Category.objects.get_or_create(
                slug='amigurumis',
                defaults={'name': 'Amigurumis', 'description': 'Muñecos y figuras tejidas a ganchillo con todo el cariño'}
            )[0],
            'bolsos': Category.objects.get_or_create(
                slug='bolsos-y-bolsas',
                defaults={'name': 'Bolsos y bolsas', 'description': 'Bolsos, clutches y bolsas tejidas para el día a día'}
            )[0],
            'accesorios': Category.objects.get_or_create(
                slug='accesorios',
                defaults={'name': 'Accesorios', 'description': 'Complementos únicos: diademas, scrunchies, bisutería'}
            )[0],
            'hogar': Category.objects.get_or_create(
                slug='hogar',
                defaults={'name': 'Hogar', 'description': 'Decoración y detalles para hacer tu casa más acogedora'}
            )[0],
        }

        self.stdout.write('Creando productos...')
        products_data = [
            {
                'name': 'Osito Dormilón',
                'slug': 'osito-dormilon',
                'description': 'Un adorable osito de peluche tejido a mano, perfecto para acompañar los dulces sueños de los más pequeños. Relleno con fibra hipoalergénica y tejido en algodón orgánico. Mide aproximadamente 30cm y viene con su gorrito de dormir intercambiable.',
                'category': categories['amigurumis'],
                'price_custom_order': 55.00,
                'price_kit': 22.00,
                'is_customizable': True,
                'customization_options': 'Beige, Rosa pastel, Azul cielo, Lavanda, Menta',
                'video_url': 'https://www.youtube.com/watch?v=example1',
            },
            {
                'name': 'Unicornio Arcoíris',
                'slug': 'unicornio-arcoiris',
                'description': 'Nuestro unicornio más mágico: crin multicolor, cuerno dorado y una expresión que enamora. Cada uno tiene su propia personalidad. Ideal como regalo especial o decoración para la habitación infantil. Aproximadamente 35cm de altura.',
                'category': categories['amigurumis'],
                'price_custom_order': 75.00,
                'price_kit': 25.00,
                'is_customizable': True,
                'customization_options': 'Blanco clásico, Rosa, Lila, Azul celeste',
                'video_url': 'https://www.youtube.com/watch?v=example2',
            },
            {
                'name': 'Pulpo Emoción',
                'slug': 'pulpo-emocion',
                'description': 'Inspirado en los pulpos terapéuticos para bebés prematuros, este amigurumi tiene tentáculos rizados que recuerdan al cordón umbilical. Cada pulpo tiene una expresión diferente. Perfecto como primer peluche.',
                'category': categories['amigurumis'],
                'price_custom_order': 35.00,
                'price_kit': 15.00,
                'is_customizable': True,
                'customization_options': 'Coral, Turquesa, Amarillo, Morado, Verde menta',
                'video_url': 'https://www.youtube.com/watch?v=example3',
            },
            {
                'name': 'Tote Bag Boho',
                'slug': 'tote-bag-boho',
                'description': 'Bolso tipo tote tejido en cuerda de algodón natural con un diseño calado precioso. Perfecto para la playa, el mercado o el día a día. Interior con bolsillo. Asas largas para llevar al hombro. Colores naturales que combinan con todo.',
                'category': categories['bolsos'],
                'price_custom_order': 65.00,
                'price_kit': 28.00,
                'is_customizable': True,
                'customization_options': 'Natural, Terracota, Arena, Oliva',
                'video_url': 'https://www.youtube.com/watch?v=example4',
            },
            {
                'name': 'Clutch Fiesta',
                'slug': 'clutch-fiesta',
                'description': 'Un clutch elegante tejido con hilo brillante, perfecto para eventos especiales. Cierre con botón magnético, cadena desmontable incluida. Forro interior de tela de algodón. Combina artesanía con glamour.',
                'category': categories['bolsos'],
                'price_custom_order': 48.00,
                'price_kit': 20.00,
                'is_customizable': True,
                'customization_options': 'Dorado, Plateado, Rosa nude, Negro',
                'video_url': 'https://www.youtube.com/watch?v=example5',
            },
            {
                'name': 'Set Diademas Primavera',
                'slug': 'set-diademas-primavera',
                'description': 'Pack de 3 diademas tejidas con diseños florales diferentes. Ideales para niñas y adultas. Elásticas y cómodas, no aprietan. Cada diadema tiene una flor o motivo diferente que se puede personalizar.',
                'category': categories['accesorios'],
                'price_custom_order': 28.00,
                'price_kit': 15.00,
                'is_customizable': True,
                'customization_options': 'Pastel mix, Tierra mix, Brights mix',
                'video_url': 'https://www.youtube.com/watch?v=example6',
            },
            {
                'name': 'Cesta Organizadora XL',
                'slug': 'cesta-organizadora-xl',
                'description': 'Cesta grande tejida en trapillo con base rígida, perfecta para organizar mantas, cojines, juguetes o revistas. Estructura firme que mantiene la forma. Con asas reforzadas. Diámetro 35cm, altura 25cm.',
                'category': categories['hogar'],
                'price_custom_order': 45.00,
                'price_kit': 22.00,
                'is_customizable': True,
                'customization_options': 'Gris perla, Blanco roto, Mostaza, Verde bosque',
                'video_url': 'https://www.youtube.com/watch?v=example7',
            },
            {
                'name': 'Posavasos Mandala (Set 4)',
                'slug': 'posavasos-mandala-set-4',
                'description': 'Set de 4 posavasos con diseño de mandala, cada uno en un color diferente pero coordinados entre sí. Tejidos en hilo de algodón con almidonado para mayor rigidez. Diámetro 10cm. Lavables a mano.',
                'category': categories['hogar'],
                'price_custom_order': 22.00,
                'price_kit': 12.00,
                'is_customizable': True,
                'customization_options': 'Tonos tierra, Tonos pastel, Tonos naturales',
                'video_url': 'https://www.youtube.com/watch?v=example8',
            },
        ]

        for data in products_data:
            Product.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )

        self.stdout.write('Creando configuración del sitio...')
        SiteConfiguration.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'Lazadas',
                'tagline': 'Creaciones únicas hechas con amor y hilo',
                'about_text': 'Somos un pequeño taller artesanal donde cada pieza se teje con dedicación y mimo.',
                'email': 'hola@lazadas.es',
                'instagram_url': 'https://instagram.com/lazadas_crochet',
            }
        )

        self.stdout.write(self.style.SUCCESS(
            '✓ Datos de ejemplo cargados correctamente:\n'
            f'  - {Category.objects.count()} categorías\n'
            f'  - {Product.objects.count()} productos\n'
            f'  - Configuración del sitio creada'
        ))
