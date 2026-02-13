from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationEmailView,
    UserProfileImageView,
    VerifyEmailView,
)

app_name = "users"

DecoratedTokenRefreshView = extend_schema(tags=["auth"], auth=[])(TokenRefreshView)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path(
        "auth/token/refresh/",
        DecoratedTokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path("auth/email/verify/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "auth/email/resend/",
        ResendVerificationEmailView.as_view(),
        name="resend-verification",
    ),
    path(
        "auth/password/change/",
        PasswordChangeView.as_view(),
        name="password-change",
    ),
    path(
        "auth/password/reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "users/me/profile-image/",
        UserProfileImageView.as_view(),
        name="profile-image",
    ),
]
