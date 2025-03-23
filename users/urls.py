from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import register_user, health_check, mobile_login
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", register_user, name="register_user"),
    path("auth/login/", mobile_login, name="mobile_login"),
    path("health-check/", health_check, name="health_check"),
]
