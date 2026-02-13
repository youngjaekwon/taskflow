import pytest
from django.urls import reverse

LOGIN_URL = reverse("users:login")


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, api_client, verified_user):
        response = api_client.post(
            LOGIN_URL,
            {"email": verified_user.email, "password": "testpass123!"},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        user_data = response.data["user"]
        assert user_data["id"] == verified_user.id
        assert user_data["email"] == verified_user.email
        assert "username" in user_data
        assert "first_name" in user_data
        assert "last_name" in user_data

    def test_login_wrong_password(self, api_client, verified_user):
        response = api_client.post(
            LOGIN_URL,
            {"email": verified_user.email, "password": "wrongpass"},
            format="json",
        )
        assert response.status_code == 400

    def test_login_nonexistent_user(self, api_client):
        response = api_client.post(
            LOGIN_URL,
            {"email": "ghost@example.com", "password": "testpass123!"},
            format="json",
        )
        assert response.status_code == 400

    def test_login_email_not_verified(self, api_client, user_factory):
        user_factory(email="unverified@example.com", email_verified=False)
        response = api_client.post(
            LOGIN_URL,
            {"email": "unverified@example.com", "password": "testpass123!"},
            format="json",
        )
        assert response.status_code == 400
