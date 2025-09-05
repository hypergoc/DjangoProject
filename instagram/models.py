from django.db import models

class InstagramPost(models.Model):
    instagram_id = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True, null=True)
    post_url = models.URLField(max_length=256, unique=True)
    post_image = models.URLField(max_length=512)
    published = models.BooleanField(default=False)
    publish_date = models.DateTimeField()
    post_song = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return f"Post {self.instagram_id}"

    class Meta:
        verbose_name = "Instagram Post"
        verbose_name_plural = "Instagram Posts"
        ordering = ['-publish_date']