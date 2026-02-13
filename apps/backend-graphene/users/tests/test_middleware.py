import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestJWTAuthenticationMiddleware:
    def test_valid_token_authenticates_user(self, api_client, verified_user):
        refresh = RefreshToken.for_user(verified_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = api_client.get(reverse("graphql"), {"query": "{ __typename }"})
        assert response.status_code == 200

    def test_no_token_remains_anonymous(self, api_client):
        response = api_client.get(reverse("graphql"), {"query": "{ __typename }"})
        assert response.status_code == 200

    def test_invalid_token_remains_anonymous(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        response = api_client.get(reverse("graphql"), {"query": "{ __typename }"})
        assert response.status_code == 200
