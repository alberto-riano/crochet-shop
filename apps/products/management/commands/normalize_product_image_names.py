from django.core.management.base import BaseCommand

from apps.products.models import Product, ProductImage, _normalized_extension


class Command(BaseCommand):
    help = 'Renombra imágenes de productos al formato ID_Categoria_Nombre_XX en storage y actualiza la BD.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra los cambios sin escribir en storage ni BD.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        total_changes = 0

        for product in Product.objects.select_related('category').all():
            if product.cover_image:
                ext = _normalized_extension(product.cover_image.name)
                target = product._build_cover_filename(ext)
                total_changes += self._rename_field(product, 'cover_image', target, dry_run)

            for image in product.images.all().order_by('order', 'id'):
                if not image.image:
                    continue
                ext = _normalized_extension(image.image.name)
                target = product.build_gallery_filename(image.order or 1, ext)
                total_changes += self._rename_field(image, 'image', target, dry_run)

        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: {total_changes} cambios detectados.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Completado: {total_changes} archivos normalizados.'))

    def _rename_field(self, instance, field_name, target_name, dry_run):
        field_file = getattr(instance, field_name)
        current_name = field_file.name
        if not current_name or current_name == target_name:
            return 0

        storage = field_file.storage
        if not storage.exists(current_name):
            self.stdout.write(self.style.WARNING(f'No existe en storage: {current_name}'))
            return 0

        self.stdout.write(f'{current_name} -> {target_name}')
        if dry_run:
            return 1

        if storage.exists(target_name):
            storage.delete(target_name)

        with storage.open(current_name, 'rb') as source:
            storage.save(target_name, source)

        setattr(instance, field_name, target_name)
        instance.save(update_fields=[field_name])
        storage.delete(current_name)
        return 1
