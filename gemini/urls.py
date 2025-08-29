# gemini/urls.py

from django.urls import path
from . import views

app_name = 'gemini'

urlpatterns = [
    # Ovdje povezujemo URL 'chat/' s našim novim view-om
    # Adresa će biti npr. http://127.0.0.1:8000/gemini/chat/
    path('chat/', views.chat_interface_view, name='chat_interface'),
]