# imagen/management/commands/import_prompts.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from imagen.models import ContentGeneration as Model
import shutil

INPUT_FOLDER = os.path.join('data', 'sorted')
OUTPUT_FOLDER = os.path.join('data', 'prompts')

class Command(BaseCommand):
    # Updated help text to reflect the new recommended structure
    help = "Imports prompt into model"

    def handle(self, *args, **options):
        full_path = settings.BASE_DIR / INPUT_FOLDER
        move_path = settings.BASE_DIR / OUTPUT_FOLDER

        if not os.path.isdir(full_path):
            self.stdout.write(self.style.ERROR(f'Directory "{full_path}" does not exist.'))
            return

        self.stdout.write(f'Scanning directory: {full_path}')
        file_extensions = ['.txt']
        files_found = 0
        files_imported = 0

        for filename in os.listdir(full_path):
            if any(filename.lower().endswith(ext) for ext in file_extensions):
                files_found += 1
                file_path = os.path.join(full_path, filename)

                with open(file_path,'r') as file:
                    content = file.read().replace('\n', '')

                file.close()

                created = Model.objects.create(prompt=content)

                if created.id:
                    files_imported +=1
                    shutil.move(file_path, move_path / filename)
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped "{filename}", already exists in DB.'))

        self.stdout.write(self.style.SUCCESS(f'Scan complete. Found {files_found} prompts, imported {files_imported} new prompts.'))