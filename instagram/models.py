from django.db import models

class InstagramPost(models.Model):
    instagram_id = models.CharField(max_length=255, unique=True, verbose_name="Instagram ID")
    content = models.TextField(blank=True, null=True, verbose_name="Opis")
    post_url = models.URLField(max_length=500, blank=True, verbose_name="URL objave")
    # Promjena: URLField je postao FileField za lokalno spremanje slika
    post_image = models.FileField(upload_to='IG/', max_length=512, blank=True, verbose_name="Slika")
    publish_date = models.DateTimeField(null=True, blank=True, verbose_name="Datum objave")
    published = models.BooleanField(default=False, verbose_name="Objavljeno")
    post_song = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pjesma")
    
    comment_count = models.PositiveIntegerField(default=0, verbose_name="Broj komentara")
    like_count = models.PositiveIntegerField(default=0, verbose_name="Broj lajkova")

    class Meta:
        ordering = ['-publish_date']
        verbose_name = "Instagram objava"
        verbose_name_plural = "Instagram objave"

    def __str__(self):
        return f"Objava {self.instagram_id} od {self.publish_date.strftime('%Y-%m-%d') if self.publish_date else 'N/A'}"