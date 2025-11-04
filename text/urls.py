from django.urls import path
from . import views

app_name = 'text'

urlpatterns = [
    path('add/', views.add_texts_view, name='add_texts'),
]