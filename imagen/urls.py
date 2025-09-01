from django.urls import path
from . import views

# app_name je ključan kako bi Django znao gdje tražiti url ime 'ajax_gemini_request'
app_name = 'imagen'

urlpatterns = [
    # Ova linija povezuje URL /imagen/ajax/gemini-request/ s tvojim viewom
    path('ajax/gemini-request/', views.gemini_request_view, name='ajax_gemini_request'),
]