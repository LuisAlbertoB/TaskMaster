from rest_framework import viewsets, permissions
from src.models import Tag
from src.services.tag_serializer import TagSerializer


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
