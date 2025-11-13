import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

# Definiramo koje ekstenzije smatramo slikama
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')


class Command(BaseCommand):
    help = 'Renames all image files in a given directory to a sequential format (001.ext, 002.ext, etc.).'

    def add_arguments(self, parser):
        # Ovdje definiramo argument 'path' koji si spomenuo
        parser.add_argument('path', type=str, help='The full path to the directory containing images.')

    def handle(self, *args, **options):
        full_path = full_path = settings.BASE_DIR / options['path']

        # Provjera postoji li zadani direktorij
        if not os.path.isdir(full_path):
            self.stderr.write(self.style.ERROR(f'Error: Directory not found at "{full_path}"'))
            sys.exit(1)

        self.stdout.write(f'Scanning directory: {full_path}')

        images_found = 0
        images_renamed = 0

        # << POCETAK TVOG DIJELA >>

        # Sortiramo listu datoteka da osiguramo konzistentan redoslijed
        files_to_process = sorted(os.listdir(full_path))

        for filename in files_to_process:
            # Provjeravamo je li datoteka slika
            if filename.lower().endswith(IMAGE_EXTENSIONS):
                images_found += 1

                # 1. Odvajamo ekstenziju od imena datoteke
                file_root, file_extension = os.path.splitext(filename)

                # 2. Stvaramo novo ime koristeći brojač. `{images_renamed + 1:03d}` formatira broj kao 001, 002, itd.
                new_filename = f"{images_renamed + 1:03d}{file_extension}"

                # 3. Sastavljamo punu staru i novu putanju
                old_filepath = os.path.join(full_path, filename)
                new_filepath = os.path.join(full_path, new_filename)

                # 4. Ako novo ime već ne postoji, preimenuj datoteku
                if not os.path.exists(new_filepath):
                    try:
                        os.rename(old_filepath, new_filepath)
                        self.stdout.write(f'Renamed: "{filename}" -> "{new_filename}"')
                        images_renamed += 1
                    except OSError as e:
                        self.stderr.write(self.style.ERROR(f'Error renaming "{filename}": {e}'))
                else:
                    # Ovo je sigurnosna provjera ako npr. 001.jpg već postoji
                    self.stdout.write(self.style.WARNING(f'Skipped: "{new_filename}" already exists.'))

        # << KRAJ TVOG DIJELA >>

        self.stdout.write(
            self.style.SUCCESS(f'Scan complete. Found {images_found} images, renamed {images_renamed} images.'))