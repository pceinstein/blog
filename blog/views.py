from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.

# obter todas as postagens cujo status seja published
def post_list(request):
    posts = Post.published.all()
    
    return render(request,
        'blog/post/list.html',
        {'posts': posts})


# mostrar uma única postagem
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, 
        	status='published',
            publish__year=year,
            publish__month=month,
            publish__day=day)
    
    return render(request,
        'blog/post/detail.html',
        {'post':post})