from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F
from .models import Post

def home(request):
    q = request.GET.get("q", "").strip()
    posts = Post.objects.all()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(body_md__icontains=q))
    paginator = Paginator(posts, 9)  # 每页 9 篇，卡片好看
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    ctx = {"posts": page_obj, "q": q}
    return render(request, "home.html", ctx)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # 计数：避免并发问题，用 F 表达式
    Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
    post.refresh_from_db()
    return render(request, "post_detail.html", {"post": post})
