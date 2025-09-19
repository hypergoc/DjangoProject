# init server
python manage.py runserver

# migratioins
python manage.py makemigrations
python manage.py migrate

# settings.py MariaDB

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myprojectdb',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306', # Default port for MySQL
    }
}

# requirements
pip freeze -l > requirements.txt
pip install -r requirements.txt

# adminuser create
python manage.py createsuperuser

# new app
python manage.py startapp gallery

# myproject/settings.py
INSTALLED_APPS = [
    # ... other apps
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'gallery', # Add our new app here
]

# gallery/models.py
from django.db import models

class Image(models.Model):

# bash
python manage.py makemigrations gallery
python manage.py migrate

# gallery/admin.py
from django.contrib import admin
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):

http://127.0.0.1:8000/admin/

# gallery/urls.py
from django.urls import path
from . import views

app_name = 'gallery' # Good practice to namespace your app's URLs

urlpatterns = [
    path('', views.gallery_view, name='gallery_display'),
]

# myproject/urls.py
path('gallery/', include('gallery.urls', namespace='gallery')), # Add this line

# gallery/views.py
from django.shortcuts import render
from .models import Image

def gallery_view(request):
    # The .all() will automatically use the 'ordering' from the model's Meta class
    images = Image.objects.all()
    context = {
        'images': images,
    }
    return render(request, 'gallery/gallery.html', context)

# add html 
gallery/templates/gallery/gallery.html

# myproject/settings.py

# URL to access media files from the browser
MEDIA_URL = '/media/'

# Absolute path to the directory where media files will be stored
MEDIA_ROOT = BASE_DIR / 'media'

# commands
create management/commands/import_images.py

# init import command
python manage.py import_images "C:\path\to\your\images"










