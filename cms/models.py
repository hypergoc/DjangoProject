from django.db import models
from django.utils import timezone

class PostCategory(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name = "Post Category"
        verbose_name_plural = "Post Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(PostCategory, related_name='posts', blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    published = models.BooleanField(default=True)
    date_of_publishing = models.DateTimeField(default=timezone.now)
    share_on_instagram = models.BooleanField(default=False)
    share_on_facebook = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_of_publishing']

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_path = models.ImageField(upload_to='post_images/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for post: {self.post.title}"