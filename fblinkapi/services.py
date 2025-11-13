import os
import sys
import logging

from httplib2.auth import params

from settings.models import Setting
from linkedin_api import Linkedin

# Postavke za ispis u stdout, korisno za management komande
logger = logging.getLogger(__name__)
# Provjera da se handler ne dodaje više puta
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')  # Jednostavniji format
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def linkedin_login():
    try:
        email = Setting.objects.get(path='linkedin/email')
        password = Setting.objects.get(path='linkedin/password')
        profile_id = Setting.objects.get(path='linkedin/profile')

        # Autentifikacija
        client = Linkedin(email, password)
        return client

    except Exception as e:
        raise print(f"Dogodila se greška prilikom komunikacije s LinkedIn API-jem: {e}")


def send_post_to_linkedin():
    try:
        data = {
            "author": "urn:li:person:302192488",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": "Learning more about LinkedIn by reading the LinkedIn Blog!"
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Official LinkedIn Blog - Your source for insights and information about LinkedIn."
                            },
                            "originalUrl": "https://blog.linkedin.com/",
                            "title": {
                                "text": "Official LinkedIn Blog"
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        client = linkedin_login()

        print(client)



        post = client._post(
            uri=Setting.objects.get(path='linkedin/posturl'),
            params=data
        )

        print(post);

    except Exception as e:
        raise print(f"Dogodila se greška prilikom komunikacije s LinkedIn API-jem: {e}")
