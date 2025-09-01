# gallery/views.py
from django.shortcuts import render
from .models import Image
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


def gallery_view(request):
    # The .all() will automatically use the 'ordering' from the model's Meta class
    # images = Image.objects.all()
    images = Image.objects.filter(is_disabled=False)
    context = {
        'images': images,
    }
    return render(request, 'gallery/gallery.html', context)


@require_POST
def save_image_order(request):
    """ AJAX view za spremanje novog redoslijeda slika. """
    try:
        # Očekujemo listu ID-jeva u 'order' parametru
        image_ids = json.loads(request.POST.get('order'))

        # Prolazimo kroz listu i ažuriramo 'order' polje za svaku sliku
        for index, image_id in enumerate(image_ids):
            Image.objects.filter(pk=image_id).update(order=index)

        return JsonResponse({'status': 'success', 'message': 'Redoslijed je uspješno spremljen.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_POST
def toggle_disable_status(request):
    """ AJAX view za paljenje/gašenje 'is_disabled' statusa. """
    try:
        image_id = request.POST.get('image_id')
        image = get_object_or_404(Image, pk=image_id)

        # Okreni boolean vrijednost
        image.is_disabled = not image.is_disabled
        image.save()

        return JsonResponse({'status': 'success', 'new_state': image.is_disabled})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
