import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

RESET_REQUEST_URL = reverse("users:password-reset-request")
RESET_CONFIRM_URL = reverse("users:password-reset-confirm")


@pytest.mark.django_db
class TestPasswordResetRequestView:
    def test_reset_request_sends_email(self, api_client, verified_user):
        response = api_client.post(
            RESET_REQUEST_URL, {"email": verified_user.email}, format="json"
        )
        assert response.status_code == 200
        assert len(mail.outbox) == 1

    def test_reset_request_nonexistent_email(self, api_client):
        response = api_client.post(
            RESET_REQUEST_URL, {"email": "ghost@example.com"}, format="json"
        )
        assert response.status_code == 200  # 보안: 성공 응답
        assert len(mail.outbox) == 0


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    def test_reset_confirm_success(self, api_client, verified_user):
        uid = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = default_token_generator.make_token(verified_user)
        response = api_client.post(
            RESET_CONFIRM_URL,
            {
                "uid": uid,
                "token": token,
                "new_password": "ResetStrong789!",
                "new_password_confirm": "ResetStrong789!",
            },
            format="json",
        )
        assert response.status_code == 200
        verified_user.refresh_from_db()
        assert verified_user.check_password("ResetStrong789!")

    def test_reset_confirm_password_mismatch(self, api_client, verified_user):
        uid = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = default_token_generator.make_token(verified_user)
        response = api_client.post(
            RESET_CONFIRM_URL,
            {
                "uid": uid,
                "token": token,
                "new_password": "ResetStrong789!",
                "new_password_confirm": "DifferentPass456!",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "new_password_confirm" in response.data

    def test_reset_confirm_invalid_token(self, api_client, verified_user):
        uid = urlsafe_base64_encode(force_bytes(verified_user.pk))
        response = api_client.post(
            RESET_CONFIRM_URL,
            {
                "uid": uid,
                "token": "bad-token",
                "new_password": "ResetStrong789!",
                "new_password_confirm": "ResetStrong789!",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_reset_confirm_invalid_uid(self, api_client):
        response = api_client.post(
            RESET_CONFIRM_URL,
            {
                "uid": "bad-uid",
                "token": "bad-token",
                "new_password": "ResetStrong789!",
                "new_password_confirm": "ResetStrong789!",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_reset_confirm_invalidates_old_tokens(self, api_client, verified_user):
        old_refresh = RefreshToken.for_user(verified_user)
        uid = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = default_token_generator.make_token(verified_user)
        api_client.post(
            RESET_CONFIRM_URL,
            {
                "uid": uid,
                "token": token,
                "new_password": "ResetStrong789!",
                "new_password_confirm": "ResetStrong789!",
            },
            format="json",
        )
        refresh_response = api_client.post(
            reverse("users:token-refresh"),
            {"refresh": str(old_refresh)},
            format="json",
        )
        assert refresh_response.status_code == 401
