from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
import json
from .models import ContentGeneration
from . import services as imagen_services

@staff_member_required
@require_POST
def gemini_request_view(request):
    try:
        data = json.loads(request.body)
        gemini_text = data.get('gemini_request_text')
        object_id = data.get('object_id')

        if not gemini_text:
            return JsonResponse({'success': False, 'error': 'Gemini request text is empty.'}, status=400)

        ai_response_text, p_tokens, c_tokens = imagen_services.get_gemini_text_response(gemini_text)

        if object_id:
            obj = ContentGeneration.objects.get(pk=object_id)
        else:
            obj = ContentGeneration()

        obj.gemini_request = gemini_text
        obj.prompt = ai_response_text
        obj.prompt_tokens = p_tokens
        obj.completion_tokens = c_tokens
        obj.save()

        return JsonResponse({'success': True, 'prompt': obj.prompt, 'new_object_id': obj.pk})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@staff_member_required
@require_POST
def imagen_request_view(request):
    try:
        data = json.loads(request.body)
        object_id = data.get('object_id')
        if not object_id:
            return JsonResponse({'success': False, 'error': 'Object ID is missing.'}, status=400)

        obj = ContentGeneration.objects.get(pk=object_id)
        imagen_services.generate_imagen_image(obj)
        
        # Osvježi objekt iz baze da dobiješ sve slike
        obj.refresh_from_db()
        
        # Renderiraj HTML za galeriju i pošalji ga nazad
        images_html = render_to_string(
            'admin/imagen/partials/image_gallery_grid.html', 
            {'images': obj.path.images.all()}
        )

        return JsonResponse({
            'success': True, 
            'images_html': images_html,
            'new_image_count': obj.image_count
        })

    except ContentGeneration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Object not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)