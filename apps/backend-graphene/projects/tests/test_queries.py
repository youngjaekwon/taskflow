import json

import pytest
from django.urls import reverse

from conftest import make_auth_client
from organizations.models import OrganizationMembership, Role
from projects.models import ProjectMembership

GRAPHQL_URL = reverse("graphql")

PROJECT_DETAIL_QUERY = """
    query Project($id: ID!) {
        project(id: $id) {
            id
            name
            slug
            description
            organization {
                id
            }
            members {
                user {
                    id
                    email
                }
                joinedAt
            }
            createdBy {
                id
            }
        }
    }
"""

PROJECTS_LIST_QUERY = """
    query Projects($organizationId: ID!) {
        projects(organizationId: $organizationId) {
            id
            name
            slug
        }
    }
"""


# ── project(id) ──


@pytest.mark.django_db
class TestProjectDetailQuery:
    def test_project_member_can_view(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECT_DETAIL_QUERY,
                    "variables": {"id": str(project_with_member.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        project_data = data["data"]["project"]
        assert project_data["name"] == project_with_member.name
        assert project_data["slug"] == project_with_member.slug

    def test_org_admin_can_view_without_project_membership(
        self, admin_user, org_with_admin, project_factory
    ):
        project = project_factory(organization=org_with_admin)
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECT_DETAIL_QUERY,
                    "variables": {"id": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["project"]["name"] == project.name

    def test_org_member_without_project_membership_cannot_view(
        self, member_user, org_with_member, project_factory
    ):
        project = project_factory(organization=org_with_member)
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECT_DETAIL_QUERY,
                    "variables": {"id": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이 프로젝트에 접근할 권한이 없습니다."

    def test_non_org_member_cannot_view(
        self, org_with_owner, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_owner)
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECT_DETAIL_QUERY,
                    "variables": {"id": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이 Organization의 멤버가 아닙니다."

    def test_unauthenticated(self, api_client, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(organization=org)
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECT_DETAIL_QUERY,
                    "variables": {"id": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_nonexistent_project(self, auth_client, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECT_DETAIL_QUERY,
                    "variables": {"id": "99999"},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "Project를 찾을 수 없습니다."

    def test_members_list_included(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        user_factory,
    ):
        other_user = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=other_user, role=Role.MEMBER
        )
        ProjectMembership.objects.create(project=project_with_member, user=other_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECT_DETAIL_QUERY,
                    "variables": {"id": str(project_with_member.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        members = data["data"]["project"]["members"]
        assert len(members) == 2


# ── projects(organizationId) ──


@pytest.mark.django_db
class TestProjectsListQuery:
    def test_admin_sees_all_projects(
        self, auth_client, verified_user, org_with_owner, project_factory
    ):
        project_factory(name="Proj A", organization=org_with_owner)
        project_factory(name="Proj B", organization=org_with_owner)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECTS_LIST_QUERY,
                    "variables": {
                        "organizationId": str(org_with_owner.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        projects = data["data"]["projects"]
        assert len(projects) == 2

    def test_member_sees_only_assigned_projects(
        self, member_user, org_with_member, project_factory
    ):
        proj_assigned = project_factory(name="Assigned", organization=org_with_member)
        project_factory(name="Not Assigned", organization=org_with_member)
        ProjectMembership.objects.create(project=proj_assigned, user=member_user)
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECTS_LIST_QUERY,
                    "variables": {
                        "organizationId": str(org_with_member.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        projects = data["data"]["projects"]
        assert len(projects) == 1
        assert projects[0]["name"] == "Assigned"

    def test_non_org_member_cannot_list(self, org_with_owner, user_factory):
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECTS_LIST_QUERY,
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

    def test_unauthenticated(self, api_client, organization_factory):
        org = organization_factory()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": PROJECTS_LIST_QUERY,
                    "variables": {
                        "organizationId": str(org.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."
