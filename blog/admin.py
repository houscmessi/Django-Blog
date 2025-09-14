from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created", "views")
    list_filter = ("created", "author", "tags")
    search_fields = ("title", "body_md")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ()
