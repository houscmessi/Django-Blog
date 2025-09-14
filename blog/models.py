from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from taggit.managers import TaggableManager

import markdown
import bleach

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "pre", "code", "img", "h1", "h2", "h3", "p", "span",
    "table", "thead", "tbody", "tr", "th", "td", "blockquote"
]
ALLOWED_ATTRS = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, "img": ["src", "alt"]}


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    excerpt = models.CharField(max_length=240, blank=True, help_text="首页摘要，可不填自动截取")
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    body_md = models.TextField()
    body_html = models.TextField(editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        raw_html = markdown.markdown(
            self.body_md, extensions=["fenced_code", "tables", "toc"]
        )
        self.body_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
        if not self.excerpt:
            # 粗略生成 40 词摘要
            self.excerpt = " ".join(self.body_md.split()[:40])
        super().save(*args, **kwargs)

    @property
    def reading_minutes(self):
        # 简单：每 350 字 ≈ 1 分钟
        return max(1, len(self.body_md) // 350)

    def __str__(self):
        return self.title
