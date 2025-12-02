from django.shortcuts import render
from .models import Post

def post_grid_view(request):
    posts = Post.objects.filter(published=True).order_by('-date_of_publishing')
    context = {
        'posts': posts
    }
    return render(request, 'cms/post_grid.html', context)