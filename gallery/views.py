# gallery/views.py
from django.shortcuts import render
from .models import Image

def gallery_view(request):
    # The .all() will automatically use the 'ordering' from the model's Meta class
    images = Image.objects.all()
    context = {
        'images': images,
    }
    return render(request, 'gallery/gallery.html', context)