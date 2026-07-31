from rest_framework import viewsets, permissions, parsers
from src.models import Tarea
from src.services.tarea_serializer import TareaSerializer
from src.middlewares.permissions import IsOwner


class TareaViewSet(viewsets.ModelViewSet):

    serializer_class = TareaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        user = self.request.user
        queryset = Tarea.objects.select_related('user', 'imagen').all()

        is_root = (
            user.is_superuser or
            (user.role is not None and user.role.permission == 'root')
        )

        # En la vista de lista (GET /api/tareas/), filtrar solo las del usuario si no es root
        if self.action == 'list' and not is_root:
            queryset = queryset.filter(user=user)

        # Filtrado opcional por ?estado=
        estado_param = self.request.query_params.get('estado')
        if estado_param is not None:
            val = estado_param.lower() in ('true', '1', 't', 'yes')
            queryset = queryset.filter(estado=val)

        # Filtrado opcional por ?prioridad=
        prioridad_param = self.request.query_params.get('prioridad')
        if prioridad_param is not None:
            try:
                queryset = queryset.filter(prioridad=int(prioridad_param))
            except ValueError:
                pass

        # Filtrado opcional por ?tag= (ID de tag)
        tag_param = self.request.query_params.get('tag')
        if tag_param is not None:
            try:
                queryset = queryset.filter(tarea_tags__tag_id=int(tag_param))
            except ValueError:
                pass

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
