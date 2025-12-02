from django.contrib import admin
from .models import PostCategory, Post, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ('image_path', 'order')
    ordering = ('order',)


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'published', 'date_of_publishing', 'created_at')
    list_filter = ('published', 'categories', 'date_of_publishing')
    search_fields = ('title', 'subtitle', 'content')
    filter_horizontal = ('categories',)
    inlines = [PostImageInline]
    date_hierarchy = 'date_of_publishing'
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'subtitle', 'content', 'categories')
        }),
        ('Publishing Options', {
            'fields': ('published', 'date_of_publishing')
        }),
        ('Social Media', {
            'fields': ('share_on_instagram', 'share_on_facebook')
        }),
    )