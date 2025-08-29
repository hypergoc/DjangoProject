# gallery/management/commands/import_images.py
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from gallery.models import Image

class Command(BaseCommand):
    # Updated help text to reflect the new recommended structure
    help = 'Imports images from a project-relative directory (e.g., "data/image") into the gallery'

    def add_arguments(self, parser):
        parser.add_argument(
            'relative_dir_path',
            type=str,
            # Updated help text for the argument
            help='The project-relative path to the directory containing images (e.g., "data/image")'
        )

    def handle(self, *args, **options):
        relative_path = options['relative_dir_path']
        full_path = settings.BASE_DIR / relative_path

        if not os.path.isdir(full_path):
            self.stdout.write(self.style.ERROR(f'Directory "{full_path}" does not exist.'))
            self.stdout.write(self.style.NOTICE(f'Please ensure you have a "{relative_path}" folder at your project root.'))
            return

        self.stdout.write(f'Scanning directory: {full_path}')
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        images_found = 0
        images_imported = 0

        for filename in os.listdir(full_path):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                images_found += 1
                image_file_path = os.path.join(full_path, filename)

                db_image_path = os.path.join('gallery_images', filename)

                _, created = Image.objects.get_or_create(path=db_image_path)

                if created:
                    image_object = Image.objects.get(path=db_image_path)
                    with open(image_file_path, 'rb') as f:
                        django_file = File(f)
                        image_object.path.save(filename, django_file, save=True)
                    images_imported += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported "{filename}"'))
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped "{filename}", already exists in DB.'))

        self.stdout.write(self.style.SUCCESS(f'Scan complete. Found {images_found} images, imported {images_imported} new images.'))