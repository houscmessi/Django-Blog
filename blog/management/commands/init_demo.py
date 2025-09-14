# blog/management/commands/init_demo.py
# 用法：
#   python manage.py init_demo
#
# 作用：
#   - 若无用户则创建超级用户 admin / admin123
#   - 生成 3 张 16:9 封面图到 MEDIA_ROOT/covers/
#   - 创建 9 篇“简历质感”文章（Markdown/代码/表格/引用/标签）
#   - 为每篇文章轮流绑定封面图
#   - 已存在相同 slug 时跳过，不重复创建
#   - 自动补足到至少 9 篇，方便首页 3×3 网格

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files import File
from blog.models import Post

from pathlib import Path

# --- 封面生成：Pillow ---
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675  # 16:9

def make_cover(path: Path, title: str, subtitle: str):
    img = Image.new("RGB", (W, H), color=(18, 18, 18))
    d = ImageDraw.Draw(img)
    title_font = ImageFont.load_default()
    sub_font = ImageFont.load_default()

    # 居中排版（简单粗暴但稳）
    def center_text(y, text, font):
        w, h = d.textbbox((0, 0), text, font=font)[2:]
        d.text(((W - w) / 2, y), text, font=font, fill=(220, 220, 220))

    center_text(int(H * 0.35), title, title_font)
    center_text(int(H * 0.47), subtitle, sub_font)
    center_text(int(H * 0.82), "Django Blog", sub_font)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")


# ----------------- 9 篇文章正文 -----------------
MD1 = """# Hello Django Blog

这是我的第一篇文章，用来记录本博客的搭建过程。

## 1. 初始化项目
```bash
django-admin startproject mysite
cd mysite
python manage.py startapp blog
```
## 2. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```
## 3. 创建超级用户
```bash
python manage.py createsuperuser
#小结：Django 自带 Admin，能让我快速管理文章和用户。
```
"""
MD2 = """# 用 Markdown 写文章的好处

Markdown 是技术写作的首选格式，原因有三点：
	1.	可读性强：语法简洁，读源码就像读文档。
	2.	版本管理方便：可以直接用 Git 跟踪改动。
	3.	跨平台：几乎所有平台都支持 Markdown 渲染。
常见 Markdown 语法:
语法 ｜ 示例        ｜ 渲染效果
标题 ｜ `# 一级标题` ｜ # 一级标题
粗体 ｜ `**text**` ｜ text
代码块 ｜ `python ...` ｜ 语法高亮
小结：Markdown 能让写作更专注于内容，而不是排版。
"""

MD3 = """# 代码高亮的重要性

技术文章少不了代码，高亮能极大提升可读性。

无高亮
```python
def add(a, b):
    return a+b
```
有高亮
```python
def add(a: int, b: int) -> int:
    return a + b

print(add(3, 5))
```
结论：当文章代码多时，高亮是必须的。
"""

MD4 = """# Django ORM 的常见查询技巧

Django 的 ORM 能帮我们用 Python 写 SQL，常见用法：

1. 筛选
```python
posts = Post.objects.filter(title__icontains="Django")
```
2. 排除
```python
posts = Post.objects.exclude(author=user)
```
3. 聚合
```python
from django.db.models import Count
tags = Tag.objects.annotate(num_posts=Count("post"))

```
SQL | ORM
SELECT * FROM post;| Post.objects.all()
WHERE title LIKE "%Django%";| .filter(title__icontains="Django")

总结：ORM 让我们少写 SQL，同时保持灵活性。
"""
MD5 = """# 为什么要加标签系统

标签（Tags）是组织文章的重要方式。
	•	分类（Category）：树状结构，适合大范围主题。
	•	标签（Tag）：自由组合，适合灵活检索。

示例
	•	一篇文章可以有：Django, Python, Web
	•	另一篇文章可以有：Docker, Python

这样读者可以很快找到同类主题的内容。

小结：标签 = 更好的导航体验。
"""

MD6 = """# 分页与搜索的实现思路

博客常见两个需求：搜索 + 分页。
搜索
```python
from django.db.models import Q
q = request.GET.get("q","")
posts = Post.objects.filter(
    Q(title__icontains=q) | Q(body_md__icontains=q)
)
```
分页
```python
from django.core.paginator import Paginator
paginator = Paginator(posts, 10)
page_obj = paginator.get_page(request.GET.get("page"))
```
搜索让用户快速定位内容，分页让页面更轻量。
"""
MD7 = """# Docker 化部署 Django 项目

为什么要 Docker 化？
	1.	一致性：开发和生产环境一致。
	2.	隔离性：避免依赖冲突。
	3.	易于部署：一条命令跑起来。

示例 Dockerfile
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn","mysite.wsgi:application","-b","0.0.0.0:8000"]
EXPOSE 8000
```
小结：Docker 是现代部署的标配。
"""
MD8 = """# CI/CD 在个人项目中的价值

CI/CD 不只属于大公司，个人项目也能用。
	•	CI（持续集成）：每次提交自动运行测试、Lint。
	•	CD（持续交付/部署）：代码合并后自动部署到服务器。
GitHub Actions 示例
```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python manage.py test
      - run: python manage.py check
      - run: python manage.py migrate
      - run: python manage.py init_demo
      - run: python manage.py runserver
        - run: echo "Deploy to server"
```
总结：CI/CD 提升开发效率，减少人为失误。
"""
MD9 = """   # 从 Demo 到生产：Render 部署经验

我把这个博客部署到了 Render，过程中的几点经验：
	1.	静态文件：需要用 Whitenoise 收集和服务。
	2.	数据库：本地用 SQLite，线上建议 Postgres。
	3.	环境变量：不要把 SECRET_KEY 放进代码里。
    4.	自动化：用 GitHub Actions 实现 CI/CD。
    5.	监控：用 Render 自带的监控功能，及时发现问题。

部署命令
	•	Build: pip install -r requirements.txt && python manage.py collectstatic --noinput
	•	Start: gunicorn mysite.wsgi:application -b 0.0.0.0:8000

总结：部署遇到的问题比写代码多，但也是学习成长的好机会。
"""
class Command(BaseCommand):
    help = "初始化"
    def handle(self, *args, **options):
        User = get_user_model()

        media_root = Path(getattr(settings, "MEDIA_ROOT", Path("media")))
        covers_dir = media_root / "covers"
        covers_dir.mkdir(parents=True, exist_ok=True)
        cover_paths = [
            covers_dir / "cover-django.png",
            covers_dir / "cover-tech.png",
            covers_dir / "cover-code.png",
        ]
        if not cover_paths[0].exists():
            make_cover(cover_paths[0], "Hello Django Blog", "Markdown • Code Highlight • Tags")
        if not cover_paths[1].exists():
            make_cover(cover_paths[1], "Tech Notes", "Search • Pagination • RSS/Sitemap")
        if not cover_paths[2].exists():
            make_cover(cover_paths[2], "Code Snippets", "REST API • Docker • CI")

        self.stdout.write(self.style.SUCCESS(f"封面已就绪：{', '.join(str(p.relative_to(media_root)) for p in cover_paths)}"))

    # 1) 用户准备
        user = User.objects.order_by("id").first()
        if not user:
            user = User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write(self.style.WARNING("未发现用户，已创建 superuser: admin / admin123"))

        posts = [
            ("hello-django-blog", "Hello Django Blog", MD1, ["django", "blog", "intro"]),
            ("markdown-benefits", "用 Markdown 写文章的好处", MD2, ["markdown", "writing"]),
            ("why-code-highlight", "代码高亮的重要性", MD3, ["markdown", "highlight"]),
            ("django-orm-tips", "Django ORM 的常见查询技巧", MD4, ["django", "orm"]),
            ("why-tags", "为什么要加标签系统", MD5, ["tag", "ux"]),
            ("search-and-pagination", "分页与搜索的实现思路", MD6, ["django", "ux"]),
            ("dockerize-django", "Docker 化部署 Django 项目", MD7, ["docker", "deploy"]),
            ("value-of-ci-cd", "CI/CD 在个人项目中的价值", MD8, ["ci", "cd", "github-actions"]),
            ("render-to-prod", "从 Demo 到生产：Render 部署经验", MD9, ["deploy", "render"]),
        ]

        created = 0
        for idx, (slug, title, body, tags) in enumerate(posts):
            if Post.objects.filter(slug=slug).exists():
                continue
            p = Post.objects.create(slug=slug, title=title, body_md=body, author=user)
            if tags:
                p.tags.add(*tags)

            with open(cover_paths[idx % len(cover_paths)], "rb") as f:
                p.cover.save(cover_paths[idx % len(cover_paths)].name, File(f), save=True)

            created += 1

        total = Post.objects.count()
        i = 1
        while total < 9:
            slug = f"sample-{i}"
            if not Post.objects.filter(slug=slug).exists():
                p = Post.objects.create(
                    slug=slug,
                    title=f"示例文章 {i}",
                    body_md="占位文章，用于补足首页网格。",
                    author=user,
                )
                p.tags.add("demo")
                with open(cover_paths[(total) % len(cover_paths)], "rb") as f:
                    p.cover.save(cover_paths[(total) % len(cover_paths)].name, File(f), save=True)
                total += 1
                created += 1
            i += 1

        self.stdout.write(self.style.SUCCESS(f"初始化完成：新建 {created} 篇文章；当前总数 {Post.objects.count()}"))
