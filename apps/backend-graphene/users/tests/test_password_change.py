import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

PASSWORD_CHANGE_URL = reverse("users:password-change")


@pytest.mark.django_db
class TestPasswordChangeView:
    def test_change_password_success(self, auth_client, verified_user):
        response = auth_client.post(
            PASSWORD_CHANGE_URL,
            {"old_password": "testpass123!", "new_password": "NewStrong456!"},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        verified_user.refresh_from_db()
        assert verified_user.check_password("NewStrong456!")

    def test_change_password_wrong_old(self, auth_client):
        response = auth_client.post(
            PASSWORD_CHANGE_URL,
            {"old_password": "wrongpass", "new_password": "NewStrong456!"},
            format="json",
        )
        assert response.status_code == 400

    def test_change_password_weak_new(self, auth_client):
        response = auth_client.post(
            PASSWORD_CHANGE_URL,
            {"old_password": "testpass123!", "new_password": "123"},
            format="json",
        )
        assert response.status_code == 400

    def test_change_password_unauthenticated(self, api_client):
        response = api_client.post(
            PASSWORD_CHANGE_URL,
            {"old_password": "testpass123!", "new_password": "NewStrong456!"},
            format="json",
        )
        assert response.status_code in (401, 403)

    def test_change_password_invalidates_old_tokens(self, auth_client, verified_user):
        old_refresh = RefreshToken.for_user(verified_user)
        auth_client.post(
            PASSWORD_CHANGE_URL,
            {"old_password": "testpass123!", "new_password": "NewStrong456!"},
            format="json",
        )
        # Old refresh token should be blacklisted
        refresh_response = APIClient().post(
            reverse("users:token-refresh"),
            {"refresh": str(old_refresh)},
            format="json",
        )
        assert refresh_response.status_code == 401
