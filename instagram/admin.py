from django.contrib import admin
from .models import InstagramPost

@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ('instagram_id', 'publish_date', 'published')
    list_filter = ('published', 'publish_date')
    search_fields = ('instagram_id', 'content', 'post_song')
    list_editable = ('published',)
    date_hierarchy = 'publish_date'