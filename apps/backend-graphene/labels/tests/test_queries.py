import json

import pytest
from django.urls import reverse

from conftest import make_auth_client

GRAPHQL_URL = reverse("graphql")


@pytest.mark.django_db
class TestLabelList:
    QUERY = """
        query Labels($organizationId: ID!) {
            labels(organizationId: $organizationId) {
                id
                name
                color
                organization {
                    id
                }
                createdBy {
                    id
                }
            }
        }
    """

    def test_success(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        label_factory,
    ):
        label_factory(organization=org_with_owner, name="Bug", created_by=verified_user)
        label_factory(
            organization=org_with_owner, name="Feature", created_by=verified_user
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "organizationId": str(org_with_owner.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        labels = data["data"]["labels"]
        assert len(labels) == 2
        label_names = [lb["name"] for lb in labels]
        assert label_names == ["Bug", "Feature"]

    def test_non_member_cannot_view(
        self, org_with_owner, label_factory, verified_user, user_factory
    ):
        label_factory(organization=org_with_owner, name="Bug", created_by=verified_user)
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "organizationId": str(org_with_owner.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이 Organization의 멤버가 아닙니다."

    def test_unauthenticated(self, api_client, org_with_owner):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "organizationId": str(org_with_owner.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."
