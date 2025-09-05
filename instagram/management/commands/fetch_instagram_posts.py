import os
import requests
from urllib.parse import urlparse
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files.base import ContentFile
from instagram.models import InstagramPost

class Command(BaseCommand):
    help = 'Fetches posts from a specific Instagram profile and saves them to the database using instagrapi.'

    def save_image_from_url(self, post_object, image_url):
        """
        Preuzima sliku s URL-a i sprema je u FileField modela.
        Ova metoda se poziva samo prilikom kreiranja novog zapisa.
        """
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            # Ekstrahiraj originalno ime datoteke i ekstenziju
            path = urlparse(image_url).path
            filename = os.path.basename(path).split('?')[0]
            file_ext = os.path.splitext(filename)[1]
            
            # Kreiraj jedinstveno ime datoteke koristeći Instagram kod objave
            unique_filename = f"{post_object.instagram_id}{file_ext if file_ext else '.jpg'}"

            # Koristi Django ContentFile za spremanje sadržaja u FileField
            image_content = ContentFile(response.content)
            
            # Spremi datoteku. Argument save=True osigurava da se i model spremi u bazu.
            post_object.post_image.save(unique_filename, image_content, save=True)
            
            self.stdout.write(self.style.SUCCESS(f"    -> Slika spremljena u {post_object.post_image.name}"))
            return True

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"    -> Neuspješno preuzimanje slike za {post_object.instagram_id}: {e}"))
            return False

    def handle(self, *args, **options):
        username = 'goczg'
        password = 'J4kazapork@'
        self.stdout.write(self.style.WARNING("Using hardcoded credentials. It's recommended to set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in settings.py"))

        cl = Client()
        cl.delay_range = [1, 3]
        session_file = "session.json"

        try:
            if os.path.exists(session_file):
                self.stdout.write(f"Loading session from {session_file}")
                cl.load_settings(session_file)
            
            self.stdout.write(f"Logging in as {username}...")
            cl.login(username, password)
            cl.dump_settings(session_file)
        except LoginRequired:
            self.stdout.write(self.style.WARNING("Session is invalid and Two-Factor Authentication is required. A code has been sent."))
            while True:
                try:
                    code = input("Enter the 2FA code: ")
                    cl.login(username, password, verification_code=code)
                    cl.dump_settings(session_file)
                    break
                except Exception as e_2fa:
                    self.stdout.write(self.style.ERROR(f"The 2FA code is incorrect or an error occurred: {e_2fa}. Please try again."))
        except Exception as e:
            raise CommandError(f"An unexpected error occurred during login: {e}")

        self.stdout.write(self.style.SUCCESS('Login successful!'))

        try:
            user_id = cl.user_id_from_username(username)
            self.stdout.write(f"Fetching posts for user ID: {user_id}...")
            posts = cl.user_medias(user_id=user_id)
        except Exception as e:
            raise CommandError(f"Failed to fetch posts for user '{username}': {e}")

        post_count = 0
        created_count = 0
        updated_count = 0

        for post in posts:
            post_count += 1
            self.stdout.write(f"Processing post: {post.code}")

            publish_datetime = post.taken_at

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

            song_title = None
            if hasattr(post, 'music_info') and post.music_info:
                song_title = post.music_info.title

            # Ažuriraj ili kreiraj zapis bez slike. Slika se dodaje naknadno samo za nove zapise.
            obj, created = InstagramPost.objects.update_or_create(
                instagram_id=post.code,
                defaults={
                    'content': post.caption_text,
                    'post_url': f"https://www.instagram.com/p/{post.code}/",
                    'publish_date': publish_datetime,
                    'post_song': song_title,
                    'like_count': post.like_count,
                    'comment_count': post.comment_count,
                }
            )

            # Ako je zapis novokreiran, preuzmi i spremi sliku.
            if created:
                if image_url:
                    self.save_image_from_url(obj, image_url)
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  > Created new post entry: {post.code}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.NOTICE(f"  > Updated existing post entry: {post.code}"))

        self.stdout.write(self.style.SUCCESS(f"\nCommand finished. Processed {post_count} posts."))
        self.stdout.write(f"New posts created: {created_count}")
        self.stdout.write(f"Existing posts updated: {updated_count}")