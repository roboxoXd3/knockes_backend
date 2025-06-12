from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterUserView,
    UserLoginView,
    VerifyOtpLoginView,
    HealthCheckView,
    LogoutUserView,
    PasswordResetView,
    UserProfileView,
    OwnerReviewListView,
    OwnerReviewCreateView,
)

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    path("auth/register/", RegisterUserView.as_view(), name="register"),
    path("auth/login/", UserLoginView.as_view(), name="user_login"),
    path("auth/verify-otp/", VerifyOtpLoginView.as_view(), name="verify-otp"),
    path("auth/logout/", LogoutUserView.as_view(), name="logout"),
    path("auth/password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("users/profile/", UserProfileView.as_view(), name="user-profile"),
    path("owners/<int:owner_id>/reviews/", OwnerReviewListView.as_view(), name="owner-review-list"),
    path("owners/<int:owner_id>/reviews/add/", OwnerReviewCreateView.as_view(), name="owner-review-create"),
]
