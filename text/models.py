from django.db import models

class TextCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Text Category"
        verbose_name_plural = "Text Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Text(models.Model):
    title = models.CharField(max_length=500)
    short_content = models.TextField(blank=True)
    content = models.TextField(blank=True)
    category = models.ForeignKey(TextCategory, on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title