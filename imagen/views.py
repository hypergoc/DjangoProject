from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
import json
from .models import ContentGeneration
from gemini import services as gemini_services

@staff_member_required
@require_POST
def gemini_request_view(request):
    try:
        data = json.loads(request.body)
        gemini_text = data.get('gemini_request_text')
        object_id = data.get('object_id')

        if not gemini_text:
            return JsonResponse({'success': False, 'error': 'Gemini request text cannot be empty.'}, status=400)

        # Pozivamo servis iz gemini aplikacije
        ai_response_text, _, _, _ = gemini_services.get_ai_response(gemini_text)

        if object_id:
            # Ažuriraj postojeći objekt
            obj = ContentGeneration.objects.get(pk=object_id)
        else:
            # Kreiraj novi objekt
            obj = ContentGeneration()

        obj.gemini_request = gemini_text
        obj.prompt = ai_response_text
        obj.save() # Sprema objekt i dobiva ID ako je novi

        return JsonResponse({
            'success': True,
            'prompt': obj.prompt,
            'new_object_id': obj.pk # Uvijek vraćamo ID
        })

    except ContentGeneration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Object not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)