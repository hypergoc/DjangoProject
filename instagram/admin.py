from django.contrib import admin
from django.utils.html import format_html
from .models import InstagramPost

@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ('instagram_id', 'publish_date', 'like_count', 'comment_count', 'published', 'image_preview_list')
    list_filter = ('published', 'publish_date')
    search_fields = ('instagram_id', 'content')
    list_editable = ('published',)
    
    readonly_fields = (
        'instagram_id', 'content', 'post_url', 'publish_date', 'post_song', 
        'like_count', 'comment_count', 'image_preview_item'
    )
    
    fieldsets = (
        ('Status', {
            'fields': ('published',)
        }),
        ('Informacije o objavi', {
            'fields': ('instagram_id', 'post_url', 'publish_date', 'like_count', 'comment_count')
        }),
        ('Sadržaj', {
            'fields': ('content', 'post_song', 'image_preview_item')
        }),
    )

    def image_preview_list(self, obj):
        """Prikaz male slike u listi (grid view)."""
        if obj.post_image:
            # Koristimo .url atribut FileField-a
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="height: 60px; width: auto;" /></a>', obj.post_image.url)
        return "Nema slike"
    image_preview_list.short_description = 'Slika'

    def image_preview_item(self, obj):
        """Prikaz veće slike u formi za uređivanje (item view)."""
        if obj.post_image:
            # Koristimo .url atribut FileField-a
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height: 300px; max-width: 300px;" /></a>', obj.post_image.url)
        return "Nema slike"
    image_preview_item.short_description = 'Pregled slike'