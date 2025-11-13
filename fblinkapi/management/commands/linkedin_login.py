from django.core.management.base import BaseCommand, CommandError
import os
from linkedin_api import Linkedin
from settings.models import Setting  # Pretpostavljamo da se model zove Setting i nalazi se u aplikaciji 'settings'
import sys
from fblinkapi import services as Service


class Command(BaseCommand):
    help = 'Prijavljuje se na LinkedIn i dohvaća podatke o profilu koristeći postavke iz baze podataka.'

    def handle(self, *args, **options):
        try:
            service = Service.send_post_to_linkedin()
        except Exception as e:
            raise CommandError(e)


        # try:
        #     email = Setting.objects.get(path='linkedin/email')
        #     password = Setting.objects.get(path='linkedin/password')
        #     profile_id = Setting.objects.get(path='linkedin/profile')
        #     self.stdout.write(self.style.SUCCESS('Postavke za LinkedIn su uspješno učitane.'))
        #     #
        #     # print(email, profile_id,password)
        #     # sys.exit(),
        #
        # except Setting.DoesNotExist as e:
        #     raise CommandError(f"Postavka nije pronađena: {e}. Molimo osigurajte da 'linkedin/email', 'linkedin/password', i 'linkedin/profile' postoje u Setting modelu.")
        # except Exception as e:
        #     raise CommandError(f"Greška prilikom učitavanja postavki: {e}")
        #
        # try:
        #     # Autentifikacija
        #     self.stdout.write(f"Pokušaj prijave s emailom: {email}")
        #     api = Linkedin(email, password)
        #     self.stdout.write(self.style.SUCCESS('Prijava na LinkedIn uspješna.'))
        #
        #     # Dohvaćanje profila
        #     self.stdout.write(f"Dohvaćanje profila: {profile_id}")
        #                                         /profile = api.get_user_profile()
        #     self.stdout.write(self.style.SUCCESS('Profil uspješno dohvaćen:'))
        #     self.stdout.write(str(profile))
        #
        #
        #
        #     # Dohvaćanje kontakt informacija
        #     # self.stdout.write(f"Dohvaćanje kontakt informacija za: {profile_id}")
        #     # contact_info = api.get_profile_contact_info(profile_id)
        #     # self.stdout.write(self.style.SUCCESS('Kontakt informacije uspješno dohvaćene:'))
        #     # self.stdout.write(str(contact_info))
        #
        # except Exception as e:
        #     raise CommandError(f"Dogodila se greška prilikom komunikacije s LinkedIn API-jem: {e}")