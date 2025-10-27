import os
import sys
import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from django.conf import settings
from django.core.management.base import CommandError
from settings.models import Setting as InstagramSetting

# Postavke za ispis u stdout, korisno za management komande
logger = logging.getLogger(__name__)
# Provjera da se handler ne dodaje više puta
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s') # Jednostavniji format
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def get_instagram_client():

    username = ''
    password = ''
    """
    Inicijalizira i prijavljuje instagrapi klijent.
    Upravlja učitavanjem/spremanjem sesije i 2FA autentikacijom.
    Vraća inicijalizirani Client objekt ili podiže CommandError.
    """
    # Preporučuje se definirati ove vrijednosti u settings.py
    try:
        model = InstagramSetting.objects.all()
        for config in model:
            if config.path == 'instagram/username':
                username = config.value
            if config.path == 'instagram/password':
                password = config.value

    except AttributeError:
        logger.warning("Upozorenje: Koriste se hardkodirani kredencijali. Preporučuje se postaviti INSTAGRAM_USERNAME i INSTAGRAM_PASSWORD u settings.py")
    # TODO:: integrate login form session file


    cl = Client()
    cl.delay_range = [1, 3]
    session_file = "session.json"

    try:
        # if os.path.exists(session_file):
        #     logger.info(f"Učitavanje sesije iz datoteke {session_file}...")
        #     cl.load_settings(session_file)
        #
        # print(username)
        # print(password)
        # print(cl)
        #
        # # sys.exit()
        logger.info(f"Prijava kao korisnik {username}...")
        cl.login(username, password)
        cl.dump_settings(session_file)
        logger.info("Prijava uspješna!")
        return cl

    except LoginRequired:
        logger.warning("Sesija je nevažeća i potrebna je dvofaktorska autentikacija. Poslan je kod.")
        while True:
            try:
                code = input("Unesite 2FA kod: ")
                cl.login(username, password, verification_code=code)
                cl.dump_settings(session_file)
                logger.info("Prijava nakon 2FA uspješna!")
                return cl
            except Exception as e_2fa:
                logger.error(f"2FA kod je netočan ili se dogodila greška: {e_2fa}. Molimo pokušajte ponovno.")
    except Exception as e:
        logger.error(f"Dogodila se neočekivana greška prilikom prijave: {e}")
        raise CommandError(f"Neuspješna prijava: {e}")