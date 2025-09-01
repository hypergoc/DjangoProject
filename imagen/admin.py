from django.contrib import admin
from .models import Path, GeneratedImage, ContentGeneration

class GeneratedImageInline(admin.TabularInline):
    model = GeneratedImage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('image_file', 'created_at')


@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ('id', 'final_prompt', 'created_at')
    search_fields = ('final_prompt',)
    inlines = [GeneratedImageInline]


@admin.register(ContentGeneration)
class ContentGenerationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'gemini_request',
        'published',
        'publishing_date',
        'order'
    )
    list_filter = ('published', 'publishing_date')
    search_fields = ('gemini_request', 'prompt', 'ig_content')
    list_editable = ('published', 'order')
    
    fieldsets = (
        ('1. Planiranje Sadržaja', {
            'fields': ('gemini_request', 'prompt')
        }),
        ('2. Generiranje Slika', {
            'fields': ('path',)
        }),
        ('3. Finalni Sadržaj i Objava', {
            'fields': ('ig_content', 'attributes', 'published', 'publishing_date', 'order')
        }),
        ('4. Metrika Uspješnosti (Read-only)', {
            'fields': ('ig_post_id', 'views', 'likes', 'comments', 'follows'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('ig_post_id', 'views', 'likes', 'comments', 'follows')