from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import register_user, user_login, verify_otp_login, health_check, logout_user, password_reset_request, reset_password, dashboard

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", register_user, name="register_user"),
    path("auth/login/", user_login, name="user_login"),
    path("auth/verify-otp/", verify_otp_login, name="verify_otp"),
    path("health-check/", health_check, name="health_check"),
    path("dashboard/", dashboard, name="dashboard"),  # ✅ Protected route
    path("auth/logout/", logout_user, name="logout"),
    path("auth/password-reset/", password_reset_request, name="password_reset_request"),
    path("auth/reset-password/", reset_password, name="reset_password"),
]
