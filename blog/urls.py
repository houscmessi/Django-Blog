from django.urls import path, include
from . import views
from .api import router as api_router

urlpatterns = [
    path("", views.home, name="home"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("api/", include(api_router.urls)),  # /api/posts/
]