from django.urls import path
from .views import post_grid_view

app_name = 'cms'

urlpatterns = [
    path('', post_grid_view, name='post_grid'),
]