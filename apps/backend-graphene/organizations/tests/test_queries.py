import json

import pytest
from django.urls import reverse

from organizations.models import OrganizationMembership, Role

GRAPHQL_URL = reverse("graphql")

MY_ORGANIZATIONS_QUERY = """
    query {
        myOrganizations {
            id
            name
            slug
            description
        }
    }
"""

ORGANIZATION_DETAIL_QUERY = """
    query Organization($id: ID!) {
        organization(id: $id) {
            id
            name
            slug
            description
            members {
                user {
                    id
                    email
                }
                role
                joinedAt
            }
        }
    }
"""


@pytest.mark.django_db
class TestMyOrganizationsQuery:
    def test_returns_user_organizations(
        self, auth_client, verified_user, organization_factory
    ):
        org1 = organization_factory(name="Org A")
        org2 = organization_factory(name="Org B")
        OrganizationMembership.objects.create(
            organization=org1, user=verified_user, role=Role.OWNER
        )
        OrganizationMembership.objects.create(
            organization=org2, user=verified_user, role=Role.MEMBER
        )

        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps({"query": MY_ORGANIZATIONS_QUERY}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        orgs = data["data"]["myOrganizations"]
        assert len(orgs) == 2

    def test_excludes_non_member_organizations(
        self, auth_client, organization_factory
    ):
        organization_factory(name="Not mine")

        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps({"query": MY_ORGANIZATIONS_QUERY}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["myOrganizations"]) == 0

    def test_unauthenticated_user(self, api_client):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps({"query": MY_ORGANIZATIONS_QUERY}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


@pytest.mark.django_db
class TestOrganizationDetailQuery:
    def test_member_can_view_organization(
        self, auth_client, verified_user, organization_factory
    ):
        org = organization_factory(name="Detail Org", description="Some desc")
        OrganizationMembership.objects.create(
            organization=org, user=verified_user, role=Role.MEMBER
        )

        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps({
                "query": ORGANIZATION_DETAIL_QUERY,
                "variables": {"id": str(org.id)},
            }),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        org_data = data["data"]["organization"]
        assert org_data["name"] == "Detail Org"
        assert org_data["description"] == "Some desc"

    def test_non_member_cannot_view_organization(
        self, auth_client, organization_factory
    ):
        org = organization_factory()

        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps({
                "query": ORGANIZATION_DETAIL_QUERY,
                "variables": {"id": str(org.id)},
            }),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이 Organization의 멤버가 아닙니다."

    def test_nonexistent_organization(self, auth_client):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps({
                "query": ORGANIZATION_DETAIL_QUERY,
                "variables": {"id": "99999"},
            }),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "Organization을 찾을 수 없습니다."

    def test_members_list_included(
        self, auth_client, verified_user, organization_factory, user_factory
    ):
        org = organization_factory()
        other_user = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org, user=verified_user, role=Role.OWNER
        )
        OrganizationMembership.objects.create(
            organization=org, user=other_user, role=Role.MEMBER
        )

        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps({
                "query": ORGANIZATION_DETAIL_QUERY,
                "variables": {"id": str(org.id)},
            }),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        members = data["data"]["organization"]["members"]
        assert len(members) == 2
