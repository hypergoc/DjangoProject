# gallery/models.py
from django.db import models

class Image(models.Model):
    # 'path' will store the image file.
    # upload_to='gallery_images/' tells Django to save uploaded images
    # into a 'gallery_images' subfolder inside your media root.
    path = models.ImageField(upload_to='gallery_images/')

    # 'order' will be used for sorting the gallery display.
    # We use PositiveIntegerField to ensure it's not negative.
    # A default value is good practice.
    order = models.PositiveIntegerField(default=0)

    class Meta:
        # This tells Django to sort query results by the 'order' field by default.
        ordering = ['order']

    def __str__(self):
        # This provides a human-readable name in the admin panel.
        return f"Image #{self.id} (Order: {self.order})"