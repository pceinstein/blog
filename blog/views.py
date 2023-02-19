from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

# obter todas as postagens cujo status seja published
def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)   # 3 postagens em cada página
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # se a página não for um inteiro, exibe a primeira página
        posts = paginator.page(1)
    except EmptyPage:
        # se a página estiver fora do intervalo,
        # exibe a última página de resultados
        posts = paginator.page(paginator.num_pages)
    
    return render(request,
        'blog/post/list.html',
        {'page':page, 'posts': posts})


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