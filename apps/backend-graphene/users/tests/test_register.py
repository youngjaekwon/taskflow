import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

User = get_user_model()

REGISTER_URL = reverse("users:register")


@pytest.mark.django_db
class TestRegisterView:
    def test_register_success(self, api_client):
        data = {
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == 201
        assert User.objects.filter(email="new@example.com").exists()

    def test_register_auto_generates_username(self, api_client):
        data = {
            "email": "auto@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        api_client.post(REGISTER_URL, data, format="json")
        user = User.objects.get(email="auto@example.com")
        assert user.username.startswith("user_")

    def test_register_sends_verification_email(self, api_client):
        data = {
            "email": "verify@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        api_client.post(REGISTER_URL, data, format="json")
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["verify@example.com"]

    def test_register_duplicate_email(self, api_client, user_factory):
        user_factory(email="dup@example.com")
        data = {
            "email": "dup@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == 400

    def test_register_weak_password(self, api_client):
        data = {
            "email": "weak@example.com",
            "password": "123",
            "password_confirm": "123",
        }
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == 400

    def test_register_password_mismatch(self, api_client):
        data = {
            "email": "mismatch@example.com",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass123!",
        }
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == 400

    def test_register_invalid_email(self, api_client):
        data = {
            "email": "not-an-email",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == 400
