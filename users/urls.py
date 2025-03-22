from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import register_user, health_check
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", register_user, name="register_user"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("health-check/", health_check, name="health_check"),
]
