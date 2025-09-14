from rest_framework import serializers, viewsets, routers
from .models import Post

class PostBriefSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "slug", "excerpt", "created", "updated", "views", "tags"]

    def get_tags(self, obj):
        return [t.name for t in obj.tags.all()]

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostBriefSerializer
    lookup_field = "slug"

router = routers.DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")