from rest_framework.routers import DefaultRouter
from src.controllers.tag_controller import TagViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = router.urls
