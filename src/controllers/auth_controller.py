from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from src.services.auth_serializer import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


