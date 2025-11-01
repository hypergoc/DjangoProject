from django.contrib import admin
from .models import Post
from django.utils.html import format_html

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'image_tag', 'published_at')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 150px; height: auto;" />'.format(obj.image.url))
        return "No Image"
    image_tag.short_description = 'Image'


admin.site.register(Post, PostAdmin)