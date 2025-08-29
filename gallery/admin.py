# gallery/admin.py
from django.contrib import admin
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'order', 'path')
    # Make the 'order' field editable directly in the list view
    list_editable = ('order',)
    # Add a filter for easy navigation if you have many images
    list_per_page = 20