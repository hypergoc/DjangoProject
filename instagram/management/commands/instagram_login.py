from django.core.management import BaseCommand
from instagrapi import Client

ACCOUNT_USERNAME="goczg"
ACCOUNT_PASSWORD='J4k4z4p0rk@'
cl = Client()

try:
    cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
    cl.dump_settings("session.json")
except Exception as e:
    print(e)

print ('success')
# user_id = cl.user_id_from_username(ACCOUNT_USERNAME)

# print(user_id)


# medias = cl.user_medias(user_id, 20)