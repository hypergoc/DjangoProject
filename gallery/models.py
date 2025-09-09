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
    order = models.PositiveIntegerField(default=0, db_index=True)

    is_disabled = models.BooleanField(default=False, db_index=True)

    used = models.BooleanField(default=False, db_index=True)

    class Meta:
        # This tells Django to sort query results by the 'order' field by default.
        ordering = ['order']

    def __str__(self):
        # This provides a human-readable name in the admin panel.
        # return f"Image #{self.id} (Order: {self.order})"
        return f"Image #{self.pk}"


SIDE_CHOICES = (
    ('L', 'Left'),
    ('R', 'Right'),
    ('T', 'Top'),
    ('B', 'Bottom'),
)

class ImageSideProfileValue(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='side_profile_values')
    side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    profile_id = models.IntegerField(null=True, blank=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"Profile for Image #{self.image_id} - {self.get_side_display()}"

class ImageConnection(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='connections_from')
    image_second = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='connections_to')
    side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    is_labeled_ai = models.BooleanField(default=False)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"Connection from Image #{self.image_id} to #{self.image_second_id}"