# gallery/admin.py
from django.contrib import admin
from .models import Image, ImageSideProfileValue, ImageConnection

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'order', 'path', 'used', 'is_disabled')
    # Make the 'order' field editable directly in the list view
    list_editable = ('order', 'used', 'is_disabled')
    # Add a filter for easy navigation if you have many images
    list_per_page = 20
    list_filter = ('used', 'is_disabled')

@admin.register(ImageSideProfileValue)
class ImageSideProfileValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'side', 'profile_id', 'value')
    list_filter = ('side',)
    search_fields = ('image__id', 'value')
    list_per_page = 20

@admin.register(ImageConnection)
class ImageConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'image_second', 'side', 'is_labeled_ai', 'value')
    list_filter = ('side', 'is_labeled_ai')
    search_fields = ('image__id', 'image_second__id', 'value')
    list_per_page = 20