import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

LOGOUT_URL = reverse("users:logout")


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_success(self, api_client, verified_user):
        refresh = RefreshToken.for_user(verified_user)
        response = api_client.post(LOGOUT_URL, {"refresh": str(refresh)}, format="json")
        assert response.status_code == 200

    def test_logout_already_blacklisted(self, api_client, verified_user):
        refresh = RefreshToken.for_user(verified_user)
        refresh.blacklist()
        response = api_client.post(LOGOUT_URL, {"refresh": str(refresh)}, format="json")
        assert response.status_code == 400

    def test_logout_without_access_token(self, api_client, verified_user):
        """로그아웃은 액세스 토큰 없이도 가능해야 한다."""
        refresh = RefreshToken.for_user(verified_user)
        # No Authorization header set
        response = api_client.post(LOGOUT_URL, {"refresh": str(refresh)}, format="json")
        assert response.status_code == 200

    def test_logout_missing_refresh(self, api_client):
        response = api_client.post(LOGOUT_URL, {}, format="json")
        assert response.status_code == 400
