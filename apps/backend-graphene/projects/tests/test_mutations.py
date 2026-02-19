import json

import pytest
from django.urls import reverse

from conftest import make_auth_client
from organizations.models import OrganizationMembership, Role
from projects.models import Project, ProjectMembership

GRAPHQL_URL = reverse("graphql")

CREATE_PROJECT = """
    mutation CreateProject($input: CreateProjectInput!) {
        createProject(input: $input) {
            project {
                id
                name
                slug
                description
                organization {
                    id
                }
                createdBy {
                    id
                }
                members {
                    user {
                        id
                    }
                }
            }
        }
    }
"""

UPDATE_PROJECT = """
    mutation UpdateProject($input: UpdateProjectInput!) {
        updateProject(input: $input) {
            project {
                id
                name
                slug
                description
            }
        }
    }
"""

DELETE_PROJECT = """
    mutation DeleteProject($id: ID!) {
        deleteProject(id: $id) {
            success
        }
    }
"""

ADD_PROJECT_MEMBER = """
    mutation AddProjectMember($input: AddProjectMemberInput!) {
        addProjectMember(input: $input) {
            projectMember {
                user {
                    id
                    email
                }
                addedBy {
                    id
                }
                joinedAt
            }
        }
    }
"""

REMOVE_PROJECT_MEMBER = """
    mutation RemoveProjectMember($input: RemoveProjectMemberInput!) {
        removeProjectMember(input: $input) {
            success
        }
    }
"""


# ── createProject ──


@pytest.mark.django_db
class TestCreateProject:
    def test_create_success(self, auth_client, verified_user, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "New Project",
                            "description": "A new project",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        project_data = data["data"]["createProject"]["project"]
        assert project_data["name"] == "New Project"
        assert project_data["slug"] == "new-project"
        assert project_data["description"] == "A new project"
        assert project_data["organization"]["id"] == str(org_with_owner.id)

    def test_creator_auto_added_as_member(
        self, auth_client, verified_user, org_with_owner
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Auto Member Project",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        project_data = data["data"]["createProject"]["project"]
        members = project_data["members"]
        assert len(members) == 1
        assert members[0]["user"]["id"] == str(verified_user.id)

    def test_admin_can_create(self, admin_user, org_with_admin):
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_admin.id),
                            "name": "Admin Project",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createProject"]["project"]["name"] == "Admin Project"

    def test_member_cannot_create(self, member_user, org_with_member):
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_member.id),
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

    def test_non_member_cannot_create(self, org_with_owner, user_factory):
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
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
        assert data["errors"][0]["message"] == "이 Organization의 멤버가 아닙니다."

    def test_unauthenticated(self, api_client, org_with_owner):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Fail",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_empty_name_validation(self, auth_client, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data

    def test_duplicate_slug_gets_suffix(
        self, auth_client, org_with_owner, project_factory
    ):
        project_factory(name="Existing", organization=org_with_owner)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_PROJECT,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Existing",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        project_data = data["data"]["createProject"]["project"]
        assert project_data["slug"] == "existing-2"


# ── updateProject ──


@pytest.mark.django_db
class TestUpdateProject:
    def test_owner_can_update(self, auth_client, org_with_owner, project_factory):
        project = project_factory(name="Original", organization=org_with_owner)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROJECT,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "name": "Updated Name",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        project_data = data["data"]["updateProject"]["project"]
        assert project_data["name"] == "Updated Name"
        assert project_data["slug"] == "updated-name"

    def test_admin_can_update(self, admin_user, org_with_admin, project_factory):
        project = project_factory(name="Admin Edit", organization=org_with_admin)
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROJECT,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "name": "Admin Updated",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateProject"]["project"]["name"] == "Admin Updated"

    def test_member_cannot_update(self, member_user, org_with_member, project_factory):
        project = project_factory(name="No Update", organization=org_with_member)
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROJECT,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
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

    def test_partial_update_description_only(
        self, auth_client, org_with_owner, project_factory
    ):
        project = project_factory(name="Keep Name", organization=org_with_owner)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROJECT,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "description": "New description",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        project_data = data["data"]["updateProject"]["project"]
        assert project_data["name"] == "Keep Name"
        assert project_data["description"] == "New description"

    def test_unauthenticated(self, api_client, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(organization=org)
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_PROJECT,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "name": "Fail",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── deleteProject ──


@pytest.mark.django_db
class TestDeleteProject:
    def test_owner_can_delete(self, auth_client, org_with_owner, project_factory):
        project = project_factory(organization=org_with_owner)
        project_id = project.id
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_PROJECT,
                    "variables": {"id": str(project_id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteProject"]["success"] is True
        assert not Project.objects.filter(pk=project_id).exists()

    def test_admin_can_delete(self, admin_user, org_with_admin, project_factory):
        project = project_factory(organization=org_with_admin)
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_PROJECT,
                    "variables": {"id": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteProject"]["success"] is True

    def test_member_cannot_delete(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_PROJECT,
                    "variables": {"id": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_cascade_deletes_memberships(
        self, auth_client, org_with_owner, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_owner)
        other_user = user_factory()
        ProjectMembership.objects.create(project=project, user=other_user)
        project_id = project.id
        auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_PROJECT,
                    "variables": {"id": str(project_id)},
                }
            ),
            content_type="application/json",
        )
        assert not ProjectMembership.objects.filter(project_id=project_id).exists()

    def test_non_member_cannot_delete(
        self, org_with_owner, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_owner)
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_PROJECT,
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
                    "query": DELETE_PROJECT,
                    "variables": {"id": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── addProjectMember ──


@pytest.mark.django_db
class TestAddProjectMember:
    def test_add_member_success(
        self, auth_client, verified_user, org_with_owner, project_factory, member_user
    ):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        project = project_factory(organization=org_with_owner)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": ADD_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(member_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        member_data = data["data"]["addProjectMember"]["projectMember"]
        assert member_data["user"]["id"] == str(member_user.id)
        assert member_data["addedBy"]["id"] == str(verified_user.id)

    def test_cannot_add_non_org_member(
        self, auth_client, org_with_owner, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_owner)
        outsider = user_factory(email_verified=True)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": ADD_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(outsider.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            data["errors"][0]["message"]
            == "해당 사용자는 이 Organization의 멤버가 아닙니다."
        )

    def test_duplicate_membership_error(
        self, auth_client, org_with_owner, project_factory, member_user
    ):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        project = project_factory(organization=org_with_owner)
        ProjectMembership.objects.create(project=project, user=member_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": ADD_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(member_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이미 이 프로젝트의 멤버입니다."

    def test_member_cannot_add(
        self, member_user, org_with_member, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_member)
        target = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org_with_member, user=target, role=Role.MEMBER
        )
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": ADD_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(target.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_unauthenticated(
        self, api_client, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        project = project_factory(organization=org)
        user = user_factory()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": ADD_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── removeProjectMember ──


@pytest.mark.django_db
class TestRemoveProjectMember:
    def test_remove_member_success(
        self, auth_client, org_with_owner, project_factory, member_user
    ):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        project = project_factory(organization=org_with_owner)
        ProjectMembership.objects.create(project=project, user=member_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(member_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["removeProjectMember"]["success"] is True
        assert not ProjectMembership.objects.filter(
            project=project, user=member_user
        ).exists()

    def test_remove_non_project_member_error(
        self, auth_client, org_with_owner, project_factory, member_user
    ):
        OrganizationMembership.objects.create(
            organization=org_with_owner, user=member_user, role=Role.MEMBER
        )
        project = project_factory(organization=org_with_owner)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(member_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이 프로젝트의 멤버가 아닙니다."

    def test_member_cannot_remove(
        self, member_user, org_with_member, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_member)
        target = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org_with_member, user=target, role=Role.MEMBER
        )
        ProjectMembership.objects.create(project=project, user=target)
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(target.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_unauthenticated(
        self, api_client, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        project = project_factory(organization=org)
        user = user_factory()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": REMOVE_PROJECT_MEMBER,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "userId": str(user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."
