from django.urls import path
from . import views

app_name = 'imagen'

urlpatterns = [
    path('ajax/gemini-request/', views.gemini_request_view, name='ajax_gemini_request'),
    path('ajax/imagen-request/', views.imagen_request_view, name='ajax_imagen_request'),
]