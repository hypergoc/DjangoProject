# gallery/urls.py
from django.urls import path
from . import views

app_name = 'gallery' # Good practice to namespace your app's URLs

urlpatterns = [
    path('', views.gallery_view, name='gallery_display'),
]