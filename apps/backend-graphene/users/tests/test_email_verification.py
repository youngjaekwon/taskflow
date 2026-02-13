import pytest
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.tokens import email_verification_token

VERIFY_URL = reverse("users:verify-email")
RESEND_URL = reverse("users:resend-verification")


@pytest.mark.django_db
class TestVerifyEmailView:
    def test_verify_success(self, api_client, user_factory):
        user = user_factory(email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        response = api_client.post(
            VERIFY_URL, {"uid": uid, "token": token}, format="json"
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email_verified is True

    def test_verify_invalid_token(self, api_client, user_factory):
        user = user_factory(email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = api_client.post(
            VERIFY_URL, {"uid": uid, "token": "bad-token"}, format="json"
        )
        assert response.status_code == 400

    def test_verify_invalid_uid(self, api_client):
        response = api_client.post(
            VERIFY_URL, {"uid": "bad-uid", "token": "bad-token"}, format="json"
        )
        assert response.status_code == 400

    def test_verify_already_verified(self, api_client, user_factory):
        user = user_factory(email_verified=True)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # Token generated against email_verified=True won't match after check
        token = email_verification_token.make_token(user)
        response = api_client.post(
            VERIFY_URL, {"uid": uid, "token": token}, format="json"
        )
        # Still succeeds (idempotent) since token was generated with current state
        assert response.status_code == 200


@pytest.mark.django_db
class TestResendVerificationEmailView:
    def test_resend_success(self, api_client, user_factory):
        user_factory(email="unverified@example.com", email_verified=False)
        response = api_client.post(
            RESEND_URL, {"email": "unverified@example.com"}, format="json"
        )
        assert response.status_code == 200
        assert len(mail.outbox) == 1

    def test_resend_already_verified(self, api_client, user_factory):
        user_factory(email="verified@example.com", email_verified=True)
        response = api_client.post(
            RESEND_URL, {"email": "verified@example.com"}, format="json"
        )
        assert response.status_code == 200
        assert len(mail.outbox) == 0

    def test_resend_nonexistent_email(self, api_client):
        response = api_client.post(
            RESEND_URL, {"email": "ghost@example.com"}, format="json"
        )
        assert response.status_code == 200  # 보안: 성공 응답
        assert len(mail.outbox) == 0
