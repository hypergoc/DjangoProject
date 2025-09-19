# gallery/urls.py
from django.urls import path
from . import views

app_name = 'gallery' # Good practice to namespace your app's URLs

urlpatterns = [
    path('', views.gallery_view, name='gallery_display'),
    path('save-order/', views.save_image_order, name='save_image_order'),
    path('toggle-disable/', views.toggle_disable_status, name='toggle_disable_status'),
    path('save-ai-connection/', views.save_ai_connection, name='save_ai_connection'),
]