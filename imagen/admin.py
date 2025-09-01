from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .models import Path, GeneratedImage, ContentGeneration
from gemini import services as gemini_services # Importamo gemini servis

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
            'fields': ('ig_content', 'attributes', 'published', 'publishing_date', 'order'),
            'classes': ('collapse',),
        }),
        ('4. Metrika Uspješnosti (Read-only)', {
            'fields': ('ig_post_id', 'views', 'likes', 'comments', 'follows'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('ig_post_id', 'views', 'likes', 'comments', 'follows')

    # --- DODAVANJE CUSTOM URL-a ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/gemini-request/', self.admin_site.admin_view(self.process_gemini_request), name='imagen_gemini_request'),
            # Ovdje može doći i URL za generiranje slika
        ]
        return custom_urls + urls

    # --- VIEW ZA OBRADU AJAX POZIVA ---
    def process_gemini_request(self, request, object_id):
        if request.method == 'POST':
            try:
                obj = self.get_object(request, object_id)
                if not obj or not obj.gemini_request:
                    return JsonResponse({'success': False, 'error': 'Nema teksta u Gemini Request polju.'}, status=400)

                # Pozivamo servis iz gemini aplikacije
                ai_response_text, _, _, _ = gemini_services.get_ai_response(obj.gemini_request)

                # Spremanje odgovora u 'prompt' polje
                obj.prompt = ai_response_text
                obj.save()

                return JsonResponse({'success': True, 'prompt': ai_response_text})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)