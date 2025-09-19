# gallery/views.py
from django.shortcuts import render
from .models import Image, ImageConnection, ImageSideProfileValue
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db import transaction


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


@require_POST
@transaction.atomic
def save_ai_connection(request):
    """ AJAX view to save AI labeled connection between two images. """
    try:
        data = json.loads(request.body)
        image1_id = data.get('image1_id')
        image2_id = data.get('image2_id')
        side = data.get('side')

        if not all([image1_id, image2_id, side]):
            return JsonResponse({'status': 'error', 'message': 'Missing data.'}, status=400)
            
        if image1_id == image2_id:
            return JsonResponse({'status': 'error', 'message': 'Cannot connect an image to itself.'}, status=400)

        image1 = get_object_or_404(Image, pk=image1_id)
        image2 = get_object_or_404(Image, pk=image2_id)

        # Define opposite sides
        opposite_sides = {'L': 'R', 'R': 'L', 'T': 'B', 'B': 'T'}
        if side not in opposite_sides:
            return JsonResponse({'status': 'error', 'message': 'Invalid side value.'}, status=400)
        opposite_side = opposite_sides[side]

        # Create connection from image1 to image2
        ImageConnection.objects.create(
            image=image1,
            image_second=image2,
            side=side,
            is_labeled_ai=True,
            value=f'Connection to image {image2.id}'
        )

        # Create the opposite connection from image2 to image1
        ImageConnection.objects.create(
            image=image2,
            image_second=image1,
            side=opposite_side,
            is_labeled_ai=True,
            value=f'Connection to image {image1.id}'
        )

        # Create profile value for image1
        ImageSideProfileValue.objects.create(
            image=image1,
            side=side,
            value=f'connected_to_{image2.id}'
        )

        # Create profile value for image2
        ImageSideProfileValue.objects.create(
            image=image2,
            side=opposite_side,
            value=f'connected_to_{image1.id}'
        )

        return JsonResponse({'status': 'success', 'message': 'AI labeled connection saved successfully.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)
    except Image.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Image not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)