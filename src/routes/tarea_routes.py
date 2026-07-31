from rest_framework.routers import DefaultRouter
from src.controllers.tarea_controller import TareaViewSet

router = DefaultRouter()
router.register(r'tareas', TareaViewSet, basename='tarea')

urlpatterns = router.urls
