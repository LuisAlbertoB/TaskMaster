from rest_framework.routers import DefaultRouter
from src.controllers.user_controller import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls
