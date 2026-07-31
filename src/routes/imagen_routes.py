from rest_framework.routers import DefaultRouter
from src.controllers.imagen_controller import ImagenViewSet

router = DefaultRouter()
router.register(r'imagenes', ImagenViewSet, basename='imagen')

urlpatterns = router.urls
