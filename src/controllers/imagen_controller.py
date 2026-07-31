from rest_framework import viewsets, permissions, parsers
from src.models import Imagen
from src.services.imagen_serializer import ImagenSerializer


class ImagenViewSet(viewsets.ModelViewSet):

    queryset = Imagen.objects.all()
    serializer_class = ImagenSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
