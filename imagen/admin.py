# gallery/admin.py
from django.contrib import admin
from .models import Path, GeneratedImage, ContentGeneration
from django.utils.html import format_html


# Admin za Path (ostaje jednostavan, za pregled)
@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ('id', 'final_prompt', 'created_at')
    list_per_page = 20


# Admin za GeneratedImage (s vlastitim previewom, korisno za debugiranje)
@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'path', 'image_preview', 'created_at')
    readonly_fields = ('image_preview',)
    list_per_page = 20

    def image_preview(self, obj):
        if obj.image_file:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image_file.url)
        return "No Image"

    image_preview.short_description = 'Image Preview'


# OVDJE JE TVOJ GLAVNI UPGRADE
@admin.register(ContentGeneration)
class ContentGenerationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'first_image_preview', 'gemini_request', 'prompt',
        'published', 'publishing_date', 'image_count', 'views', 'likes'
    )
    list_editable = ('order', 'published', 'publishing_date')
    list_filter = ('published',)
    search_fields = ('gemini_request', 'prompt', 'ig_content')
    list_per_page = 20
    # Omogućuje da se polja koja nisu direktno u modelu mogu sortirati
    readonly_fields = ('first_image_preview',)

    # OVO JE SRCE NAŠEG RJEŠENJA
    def first_image_preview(self, obj):
        """
        Prikazuje preview prve slike povezane preko Path modela.
        """
        # Prvo provjerimo ima li ContentGeneration uopće povezan Path
        if obj.path:
            # Ako ima, dohvatimo PRVU sliku iz tog Patha
            # Kroz related_name 'images'
            first_image = obj.path.images.first()

            # Ako prva slika postoji i ima file...
            if first_image and first_image.image_file:
                # Vrati HTML za prikaz slike
                return format_html('<img src="{}" style="max-height: 100px;" />', first_image.image_file.url)

        # Ako nema Patha ili nema slika, vrati poruku
        return "No Image Associated"

    first_image_preview.short_description = 'First Image Preview'