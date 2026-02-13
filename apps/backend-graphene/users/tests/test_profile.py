import json

import pytest
from django.urls import reverse

GRAPHQL_URL = reverse("graphql")


@pytest.fixture
def verified_user(user_factory):
    return user_factory(
        email_verified=True,
        first_name="Old",
        last_name="Name",
    )


ME_QUERY = """
    query {
        me {
            id
            email
            firstName
            lastName
            emailVerified
        }
    }
"""

UPDATE_PROFILE_MUTATION = """
    mutation UpdateProfile($input: UpdateProfileInput!) {
        updateProfile(input: $input) {
            user {
                firstName
                lastName
            }
        }
    }
"""


@pytest.mark.django_db
class TestMeQuery:
    def test_me_query_success(self, auth_client, verified_user):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps({"query": ME_QUERY}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["me"]["email"] == verified_user.email
        assert data["data"]["me"]["emailVerified"] is True

    def test_me_query_unauthenticated(self, api_client):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps({"query": ME_QUERY}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["me"] is None
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


@pytest.mark.django_db
class TestUpdateProfileMutation:
    def test_update_profile_success(self, auth_client, verified_user):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROFILE_MUTATION,
                    "variables": {"input": {"firstName": "New", "lastName": "Name2"}},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateProfile"]["user"]["firstName"] == "New"
        assert data["data"]["updateProfile"]["user"]["lastName"] == "Name2"
        verified_user.refresh_from_db()
        assert verified_user.first_name == "New"

    def test_update_profile_unauthenticated(self, api_client):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROFILE_MUTATION,
                    "variables": {"input": {"firstName": "New"}},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_update_profile_max_length_validation(self, auth_client, verified_user):
        long_name = "x" * 151
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROFILE_MUTATION,
                    "variables": {"input": {"firstName": long_name}},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        verified_user.refresh_from_db()
        assert verified_user.first_name == "Old"
