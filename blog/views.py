from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.db.models import Count
from taggit.models import Tag   # taggit (aplicação de terceiros)
import os

# Create your views here.

# esta classe substutui a função post_list abaixo
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


# obter todas as postagens cujo status seja published
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

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
        {'page':page, 'posts': posts, 'tag':tag})


# mostrar uma única postagem
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, 
        	status='published',
            publish__year=year,
            publish__month=month,
            publish__day=day)
    
    # Lista dos comentários ativos para esta postagem
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # Um comentário foi postado
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Cria o objeto Comment, mas não
            # o salva ainda no banco de dados
            new_comment = comment_form.save(commit=False)
            # Atribui a postagem atual ao comentário
            new_comment.post = post
            # Salva o comentário no banco de dados
            new_comment.save()

    else:   # GET request
        comment_form = CommentForm()
    
    # Lista de postagens semelhantes
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
            .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
            .order_by('-same_tags', '-publish')[:4]

    return render(request,
        'blog/post/detail.html',
        {'post':post,
         'comments':comments,
         'new_comment':new_comment,
         'comment_form':comment_form,
         'similar_posts': similar_posts})


# compartilhamento de postagens com e-mail
def post_share(request, post_id):
    # obtém a postagem com base no id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # formulário foi submetido
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # campos do formulário passaram pela validação
            cd = form.cleaned_data
            # ... envia o e-mail
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read "\
                    f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n"\
                    f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, os.environ['gmail_account'], [cd['to']])

            sent = True

    else:   # method = GET
        form = EmailPostForm()
    
    return render(request, 'blog/post/share.html',
            {'post': post, 
            'form': form,
            'sent': sent})