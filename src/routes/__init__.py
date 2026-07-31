"""
TaskMaster — Routes Package (URL Configuration principal de la API)

Reúne todas las rutas de la API bajo /api/:
  - Autenticación: /api/token/, /api/token/refresh/
  - Usuarios:      /api/users/
  - Imágenes:      /api/imagenes/
  - Tags:          /api/tags/
  - Tareas:        /api/tareas/
"""

from django.urls import path, include

urlpatterns = [
    # ─── Autenticación JWT ────────────────────────────────────────────────────
    path('', include('src.routes.auth_routes')),

    # ─── CRUDs de la API ──────────────────────────────────────────────────────
    path('', include('src.routes.user_routes')),
    path('', include('src.routes.imagen_routes')),
    path('', include('src.routes.tag_routes')),
    path('', include('src.routes.tarea_routes')),
]
