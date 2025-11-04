from django.db import models

# Create your models here.
class Text(models.Model):
    title = models.CharField(max_length=500)
    short_content = models.TextField(blank=True)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title