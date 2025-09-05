from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from instagram.models import InstagramPost
import json
import os

# Napomena: Potrebno je instalirati 'instagrapi' biblioteku
# pip install instagrapi

# Također, potrebno je dodati vaše Instagram kredencijale u settings.py datoteku:
# INSTAGRAM_USERNAME = "vas_instagram_username"
# INSTAGRAM_PASSWORD = "vasa_instagram_lozinka"

class Command(BaseCommand):
    help = 'Fetches posts from a specific Instagram profile and saves them to the database using instagrapi.'

    def handle(self, *args, **options):

        username = 'goczg'
        password = 'J4kazapork@'
        cl = Client()
        cl.delay_range = [1, 3]

        try:
            loged_in = False
            self.stdout.write(f"Logging in as {username}...")
            config_file_path = 'session.jsom'

            os.path.exists(config_file_path)

            if os.path.exists(config_file_path):
                data = cl.load_settings("session.json")
                print('logedin')
                loged_in = True
            if not loged_in:
                print('login')
                cl.login(username, password)
                cl.dump_settings("session.json")

        except LoginRequired:
            self.stdout.write(self.style.WARNING("Two-factor authentication is required. A code has been sent."))
            while True:
                try:
                    code = input("Enter the 2FA code: ")
                    cl.login(username, password, verification_code=code)
                    # Break the loop if 2FA login is successful
                    break
                except Exception as e_2fa:
                    self.stdout.write(
                        self.style.ERROR(f"The 2FA code is incorrect or an error occurred: {e_2fa}. Please try again."))
        except Exception as e:
            raise CommandError(f"An unexpected error occurred during login: {e}")

        self.stdout.write(self.style.SUCCESS('Login successful!'))

        try:
            user_id = cl.user_id_from_username(username)
            self.stdout.write(f"Fetching posts for user ID: {user_id}...")
            # amount=0 fetches all posts
            posts = cl.user_medias(user_id=user_id, amount=5)
        except Exception as e:
            raise CommandError(f"Failed to fetch posts for user '{username}': {e}")

        post_count = 0
        created_count = 0
        updated_count = 0

        print(posts)


        self.stdout.write(self.style.SUCCESS(f"\nCommand finished. Processed {post_count} posts."))
        self.stdout.write(f"New posts created: {created_count}")
        self.stdout.write(f"Existing posts updated: {updated_count}")
