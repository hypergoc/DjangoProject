import os
import requests
from urllib.parse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from instagram.models import InstagramPost, Following
from instagram.services import get_instagram_client
from instagrapi.mixins import user as Iguser
from pprint import pprint


class Command(BaseCommand):
    help = 'followers diff'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int,
            help='Limit number of instagram followers to fetch',
        )

    def handle(self, *args, **options):
        limit = 0
        if(options['limit']):
            limit = int(options['limit'])
        try:
            cl = get_instagram_client()
        except CommandError as e:
            raise e
        except Exception as e:
            raise CommandError(f"Greška prilikom inicijalizacije Instagram klijenta: {e}")

        try:
            user_id = cl.user_id_from_username(cl.username)
            self.stdout.write(f"Dohvaćanje objava za korisnika: {cl.username} (ID: {user_id})...")



            following = cl.user_followers_v1(user_id = user_id)

            for follower in following:
                model = Following.objects.create(
                    instagram_id=follower.pk,
                    username=follower.username,
                    type='followers',
                    fullname=follower.full_name
                )


            # cl.user_unfollow(user_id = user_id)

        except Exception as e:
            raise CommandError(f" {e}")
