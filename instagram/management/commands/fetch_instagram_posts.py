import os
import requests
from urllib.parse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from instagram.models import InstagramPost
from instagram.services import get_instagram_client
from pprint import pprint

class Command(BaseCommand):
    help = 'Fetches posts from a specific Instagram profile and saves them to the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int,
            help='Broj najnovijih objava za koje se dohvaća statistika.',
        )
        parser.add_argument(
            '--instagram_id', type=str,
        )

    def save_image_from_url(self, post_object, image_url):
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            path = urlparse(image_url).path
            filename = os.path.basename(path).split('?')[0]
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{post_object.instagram_id}{file_ext if file_ext else '.jpg'}"
            image_content = ContentFile(response.content)
            post_object.post_image.save(unique_filename, image_content, save=True)
            self.stdout.write(self.style.SUCCESS(f"    -> Slika spremljena u {post_object.post_image.name}"))
            return True
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"    -> Neuspješno preuzimanje slike za {post_object.instagram_id}: {e}"))
            return False

    def handle(self, *args, **options):
        limit = options['limit'] if 'limit' in options else 0
        try:
            cl = get_instagram_client()
        except CommandError as e:
            raise e
        except Exception as e:
            raise CommandError(f"Greška prilikom inicijalizacije Instagram klijenta: {e}")

        try:
            user_id = cl.user_id_from_username(cl.username)
            self.stdout.write(f"Dohvaćanje objava za korisnika: {cl.username} (ID: {user_id})...")
            posts = cl.user_medias(user_id=user_id, amount=limit) # Povećan broj za svaki slučaj
            print(posts)
        except Exception as e:
            raise CommandError(f"Neuspješno dohvaćanje objava za korisnika '{cl.username}': {e}")

        created_count, updated_count = 0, 0
        for post in posts:
            self.stdout.write(f"Obrada objave: {post.code}")
            image_url = ""
            candidates = []
            if post.media_type == 8 and post.resources:
                if hasattr(post.resources[0], 'image_versions2') and post.resources[0].image_versions2.candidates:
                    candidates = post.resources[0].image_versions2.candidates
            elif hasattr(post, 'image_versions2') and post.image_versions2.candidates:
                candidates = post.image_versions2.candidates

            if candidates:
                best_candidate = max(candidates, key=lambda c: c.width)
                image_url = best_candidate.url
            elif post.thumbnail_url:
                image_url = post.thumbnail_url

            song_title = post.music_info.title if hasattr(post, 'music_info') and post.music_info else None

            obj, created = InstagramPost.objects.update_or_create(
                instagram_id=post.code,
                defaults={
                    'instagram_pk': post.pk,
                    'content': post.caption_text,
                    'post_url': f"https://www.instagram.com/p/{post.code}/",
                    'publish_date': post.taken_at,
                    'post_song': song_title,
                }
            )

            if created:
                if image_url: self.save_image_from_url(obj, image_url)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  > Kreiran novi zapis: {post.code}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.NOTICE(f"  > Ažuriran postojeći zapis: {post.code}"))

        self.stdout.write(self.style.SUCCESS(f"\nKomanda završena. Obrađeno {len(posts)} objava."))
        self.stdout.write(f"Novih objava kreirano: {created_count}")
        self.stdout.write(f"Postojećih objava ažurirano: {updated_count}")