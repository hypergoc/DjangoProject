from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

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
    slug = models.SlugField(max_length=255, unique=True, blank=True)
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

    def get_absolute_url(self):
        return reverse('cms:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            original_slug = self.slug
            queryset = Post.objects.all().exclude(pk=self.pk)
            counter = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_path = models.ImageField(upload_to='post_images/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for post: {self.post.title}"