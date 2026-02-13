import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

REFRESH_URL = reverse("users:token-refresh")


@pytest.mark.django_db
class TestTokenRefreshView:
    def test_refresh_success(self, api_client, verified_user):
        refresh = RefreshToken.for_user(verified_user)
        response = api_client.post(
            REFRESH_URL, {"refresh": str(refresh)}, format="json"
        )
        assert response.status_code == 200
        assert "access" in response.data

    def test_refresh_invalid_token(self, api_client):
        response = api_client.post(
            REFRESH_URL, {"refresh": "invalid-token"}, format="json"
        )
        assert response.status_code == 401

    def test_refresh_blacklisted_token(self, api_client, verified_user):
        refresh = RefreshToken.for_user(verified_user)
        refresh.blacklist()
        response = api_client.post(
            REFRESH_URL, {"refresh": str(refresh)}, format="json"
        )
        assert response.status_code == 401

    def test_refresh_returns_new_refresh_token(self, api_client, verified_user):
        """토큰 갱신 시 새 refresh token이 응답에 포함된다 (rotation)."""
        refresh = RefreshToken.for_user(verified_user)
        response = api_client.post(
            REFRESH_URL, {"refresh": str(refresh)}, format="json"
        )
        assert response.status_code == 200
        assert "refresh" in response.data
        assert response.data["refresh"] != str(refresh)

    def test_old_refresh_token_blacklisted_after_rotation(self, api_client, verified_user):
        """갱신 후 이전 refresh token이 블랙리스트된다."""
        refresh = RefreshToken.for_user(verified_user)
        response = api_client.post(
            REFRESH_URL, {"refresh": str(refresh)}, format="json"
        )
        assert response.status_code == 200

        # 이전 refresh token으로 다시 갱신 시도
        response = api_client.post(
            REFRESH_URL, {"refresh": str(refresh)}, format="json"
        )
        assert response.status_code == 401
