import json

import pytest
from django.urls import reverse

from conftest import make_auth_client
from organizations.models import Organization, OrganizationMembership, Role

GRAPHQL_URL = reverse("graphql")

CREATE_ORGANIZATION = """
    mutation CreateOrganization($input: CreateOrganizationInput!) {
        createOrganization(input: $input) {
            organization {
                id
                name
                slug
                description
            }
        }
    }
"""

UPDATE_ORGANIZATION = """
    mutation UpdateOrganization($input: UpdateOrganizationInput!) {
        updateOrganization(input: $input) {
            organization {
                id
                name
                slug
                description
            }
        }
    }
"""

DELETE_ORGANIZATION = """
    mutation DeleteOrganization($id: ID!) {
        deleteOrganization(id: $id) {
            success
        }
    }
"""


@pytest.mark.django_db
class TestCreateOrganization:
    def test_create_success(self, auth_client, verified_user):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_ORGANIZATION,
                    "variables": {
                        "input": {"name": "New Org", "description": "A new org"}
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        org_data = data["data"]["createOrganization"]["organization"]
        assert org_data["name"] == "New Org"
        assert org_data["slug"] == "new-org"
        assert org_data["description"] == "A new org"

        membership = OrganizationMembership.objects.get(
            organization_id=org_data["id"], user=verified_user
        )
        assert membership.role == Role.OWNER

    def test_create_without_description(self, auth_client):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_ORGANIZATION,
                    "variables": {"input": {"name": "Minimal Org"}},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        org = data["data"]["createOrganization"]["organization"]
        assert org["name"] == "Minimal Org"

    def test_create_unauthenticated(self, api_client):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_ORGANIZATION,
                    "variables": {"input": {"name": "Fail"}},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


@pytest.mark.django_db
class TestUpdateOrganization:
    def test_owner_can_update(self, auth_client, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_ORGANIZATION,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Updated Name",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        org_data = data["data"]["updateOrganization"]["organization"]
        assert org_data["name"] == "Updated Name"
        assert org_data["slug"] == "updated-name"

    def test_admin_can_update(self, org_with_owner, admin_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_ORGANIZATION,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Admin Updated",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        org = data["data"]["updateOrganization"]["organization"]
        assert org["name"] == "Admin Updated"

    def test_member_cannot_update(self, org_with_owner, member_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_ORGANIZATION,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Should Fail",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."


@pytest.mark.django_db
class TestDeleteOrganization:
    def test_owner_can_delete(self, auth_client, org_with_owner):
        org_id = org_with_owner.id
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_ORGANIZATION,
                    "variables": {"id": str(org_id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteOrganization"]["success"] is True
        assert not Organization.objects.filter(pk=org_id).exists()

    def test_admin_cannot_delete(self, org_with_owner, admin_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=admin_user, role=Role.ADMIN
        )
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_ORGANIZATION,
                    "variables": {"id": str(org_with_owner.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_member_cannot_delete(self, org_with_owner, member_user):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_ORGANIZATION,
                    "variables": {"id": str(org_with_owner.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_cascade_deletes_memberships(
        self, auth_client, org_with_owner, user_factory
    ):
        other_user = user_factory()
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=other_user, role=Role.MEMBER
        )
        org_id = org_with_owner.id
        auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_ORGANIZATION,
                    "variables": {"id": str(org_id)},
                }
            ),
            content_type="application/json",
        )
        assert not OrganizationMembership.objects.filter(
            organization_id=org_id
        ).exists()
