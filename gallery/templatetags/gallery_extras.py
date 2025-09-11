# gallery/templatetags/gallery_extras.py

from django import template

register = template.Library()

@register.filter(name='to_resized')
def to_resized(image_url_string):
    """
    Ovaj filter uzima originalni URL slike (npr. /media/gallery_images/slika.jpg)
    i zamjenjuje 'gallery_images' s 'resized'.
    """
    if isinstance(image_url_string, str):
        return image_url_string.replace('gallery_images', 'resized')
    return image_url_string