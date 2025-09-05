from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from instagram.models import InstagramPost
import os

# Napomena: Potrebno je instalirati 'instagrapi' biblioteku
# pip install instagrapi

# Također, potrebno je dodati vaše Instagram kredencijale u settings.py datoteku:
# INSTAGRAM_USERNAME = "vas_instagram_username"
# INSTAGRAM_PASSWORD = "vasa_instagram_lozinka"

class Command(BaseCommand):
    help = 'Fetches posts from a specific Instagram profile and saves them to the database using instagrapi.'

    def handle(self, *args, **options):
        # Korištenje hardkodiranih kredencijala prema dostavljenom kodu.
        # Preporučuje se premještanje ovih vrijednosti u settings.py radi bolje sigurnosti i upravljanja konfiguracijom.
        username = 'goczg'
        password = 'J4kazapork@'
        self.stdout.write(self.style.WARNING("Using hardcoded credentials. It's recommended to set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in settings.py"))


        cl = Client()
        cl.delay_range = [1, 3]
        session_file = "session.json"

        try:
            # Učitaj sesiju ako postoji kako bi se izbjegla ponovna prijava
            if os.path.exists(session_file):
                self.stdout.write(f"Loading session from {session_file}")
                cl.load_settings(session_file)
            
            self.stdout.write(f"Logging in as {username}...")
            # login() će koristiti učitanu sesiju. Ako je sesija nevažeća ili istekla,
            # izvršit će potpunu prijavu s korisničkim imenom i lozinkom.
            cl.login(username, password)
            
            # Spremi trenutno stanje sesije u datoteku za sljedeću upotrebu
            cl.dump_settings(session_file)

        except LoginRequired:
            self.stdout.write(self.style.WARNING("Session is invalid and Two-Factor Authentication is required. A code has been sent."))
            while True:
                try:
                    code = input("Enter the 2FA code: ")
                    cl.login(username, password, verification_code=code)
                    cl.dump_settings(session_file) # Spremi sesiju nakon uspješne 2FA prijave
                    break # Izađi iz petlje u slučaju uspjeha
                except Exception as e_2fa:
                    self.stdout.write(
                        self.style.ERROR(f"The 2FA code is incorrect or an error occurred: {e_2fa}. Please try again."))
        except Exception as e:
            raise CommandError(f"An unexpected error occurred during login: {e}")

        self.stdout.write(self.style.SUCCESS('Login successful!'))

        try:
            user_id = cl.user_id_from_username(username)
            self.stdout.write(f"Fetching posts for user ID: {user_id}...")
            # amount=5 dohvaća 5 najnovijih objava
            posts = cl.user_medias(user_id=user_id, amount=5)
        except Exception as e:
            raise CommandError(f"Failed to fetch posts for user '{username}': {e}")

        post_count = 0
        created_count = 0
        updated_count = 0

        for post in posts:
            post_count += 1
            self.stdout.write(f"Processing post: {post.code}")

            # instagrapi vraća datetime objekt koji je timezone-aware (UTC)
            publish_datetime = post.taken_at

            # --- Logika za pronalaženje URL-a slike najbolje kvalitete ---
            image_url = ""
            candidates = []

            # Za karusel objave, koristimo medije iz prve stavke

            print(post.thumbnail_url)

            song_title = None
            if hasattr(post, 'music_info') and post.music_info:
                song_title = post.music_info.title

            obj, created = InstagramPost.objects.update_or_create(
                instagram_id=post.code,
                defaults={
                    'content': post.caption_text,
                    'post_url': f"https://www.instagram.com/p/{post.code}/",
                    'post_image': str(post.thumbnail_url), # Osiguraj da je URL string
                    'publish_date': publish_datetime,
                    # Polje 'published' po defaultu ostaje False kako bi se omogućila ručna provjera
                    'post_song': song_title,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  > Created new post entry: {post.code}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.NOTICE(f"  > Updated existing post entry: {post.code}"))


        self.stdout.write(self.style.SUCCESS(f"\nCommand finished. Processed {post_count} posts."))
        self.stdout.write(f"New posts created: {created_count}")
        self.stdout.write(f"Existing posts updated: {updated_count}")