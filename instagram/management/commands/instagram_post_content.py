from instagrapi import Client
from instagrapi.types import Usertag, Location
from instagram import services

client = services.get_instagram_client()




# cl.user_info_by_username('example')
#
media = client.photo_upload(
    'media/916/Google_AI_Studio_2025-09-04T10_06_01.139Z.png'
    "Test caption for photo with #hashtags and mention users such @example",
    # usertags=[Usertag(user=example, x=0.5, y=0.5)],
    # location=Location(name='Russia, Saint-Petersburg', lat=59.96, lng=30.29)
)

