import json

import pytest
from django.urls import reverse

from conftest import make_auth_client
from labels.models import Label
from organizations.models import OrganizationMembership, Role

GRAPHQL_URL = reverse("graphql")


# ── helpers ──


@pytest.fixture
def admin_user(user_factory):
    return user_factory(email_verified=True)


@pytest.fixture
def member_user(user_factory):
    return user_factory(email_verified=True)


@pytest.fixture
def org_with_admin(org_with_owner, admin_user):
    OrganizationMembership.objects.create(
        organization=org_with_owner, user=admin_user, role=Role.ADMIN
    )
    return org_with_owner


@pytest.fixture
def org_with_member(org_with_owner, member_user):
    OrganizationMembership.objects.create(
        organization=org_with_owner, user=member_user, role=Role.MEMBER
    )
    return org_with_owner


# ── TestCreateLabel ──


@pytest.mark.django_db
class TestCreateLabel:
    QUERY = """
        mutation CreateLabel($input: CreateLabelInput!) {
            createLabel(input: $input) {
                label {
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
        }
    """

    def test_success(self, auth_client, verified_user, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Bug",
                            "color": "#FF0000",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        label_data = data["data"]["createLabel"]["label"]
        assert label_data["name"] == "Bug"
        assert label_data["color"] == "#FF0000"
        assert label_data["organization"]["id"] == str(org_with_owner.id)
        assert label_data["createdBy"]["id"] == str(verified_user.id)

    def test_default_color(self, auth_client, verified_user, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Feature",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        label_data = data["data"]["createLabel"]["label"]
        assert label_data["name"] == "Feature"
        assert label_data["color"] == "#808080"

    def test_duplicate_name(self, auth_client, verified_user, org_with_owner):
        Label.objects.create(
            organization=org_with_owner,
            name="Bug",
            created_by=verified_user,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Bug",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"]

    def test_invalid_color(self, auth_client, verified_user, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Bug",
                            "color": "red",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"]

    def test_empty_name(self, auth_client, verified_user, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
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
        assert data["errors"]

    def test_member_cannot_create(self, org_with_member, member_user):
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_member.id),
                            "name": "Bug",
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
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Bug",
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
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "organizationId": str(org_with_owner.id),
                            "name": "Bug",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── TestUpdateLabel ──


@pytest.mark.django_db
class TestUpdateLabel:
    QUERY = """
        mutation UpdateLabel($input: UpdateLabelInput!) {
            updateLabel(input: $input) {
                label {
                    id
                    name
                    color
                }
            }
        }
    """

    def test_success_partial_update(
        self, auth_client, verified_user, org_with_owner, label_factory
    ):
        label = label_factory(
            organization=org_with_owner,
            name="Bug",
            color="#FF0000",
            created_by=verified_user,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "id": str(label.id),
                            "name": "Critical Bug",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        label_data = data["data"]["updateLabel"]["label"]
        assert label_data["name"] == "Critical Bug"
        assert label_data["color"] == "#FF0000"  # unchanged

    def test_update_color_only(
        self, auth_client, verified_user, org_with_owner, label_factory
    ):
        label = label_factory(
            organization=org_with_owner,
            name="Bug",
            color="#FF0000",
            created_by=verified_user,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "id": str(label.id),
                            "color": "#00FF00",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        label_data = data["data"]["updateLabel"]["label"]
        assert label_data["name"] == "Bug"  # unchanged
        assert label_data["color"] == "#00FF00"

    def test_duplicate_name(
        self, auth_client, verified_user, org_with_owner, label_factory
    ):
        label_factory(organization=org_with_owner, name="Bug", created_by=verified_user)
        other = label_factory(
            organization=org_with_owner, name="Feature", created_by=verified_user
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "id": str(other.id),
                            "name": "Bug",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"]

    def test_invalid_color(
        self, auth_client, verified_user, org_with_owner, label_factory
    ):
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "id": str(label.id),
                            "color": "invalid",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"]

    def test_member_cannot_update(
        self, org_with_member, member_user, label_factory, verified_user
    ):
        label = label_factory(
            organization=org_with_member, name="Bug", created_by=verified_user
        )
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "id": str(label.id),
                            "name": "Feature",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_nonexistent_label(self, auth_client, verified_user, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "id": "999999",
                            "name": "Bug",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "Label을 찾을 수 없습니다."

    def test_unauthenticated(
        self, api_client, org_with_owner, label_factory, verified_user
    ):
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "id": str(label.id),
                            "name": "Feature",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── TestDeleteLabel ──


@pytest.mark.django_db
class TestDeleteLabel:
    QUERY = """
        mutation DeleteLabel($id: ID!) {
            deleteLabel(id: $id) {
                success
            }
        }
    """

    def test_success(self, auth_client, verified_user, org_with_owner, label_factory):
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        label_id = label.id
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(label_id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteLabel"]["success"] is True
        assert not Label.objects.filter(pk=label_id).exists()

    def test_m2m_auto_removed(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
    ):
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        task.labels.add(label)
        assert task.labels.count() == 1

        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(label.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteLabel"]["success"] is True
        assert task.labels.count() == 0

    def test_member_cannot_delete(
        self, org_with_member, member_user, label_factory, verified_user
    ):
        label = label_factory(
            organization=org_with_member, name="Bug", created_by=verified_user
        )
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(label.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_nonexistent_label(self, auth_client, verified_user, org_with_owner):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": "999999"},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "Label을 찾을 수 없습니다."

    def test_unauthenticated(
        self, api_client, org_with_owner, label_factory, verified_user
    ):
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(label.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── TestAddLabelsToTask ──


@pytest.mark.django_db
class TestAddLabelsToTask:
    QUERY = """
        mutation AddLabelsToTask($input: AddLabelsToTaskInput!) {
            addLabelsToTask(input: $input) {
                task {
                    id
                    labels {
                        id
                        name
                    }
                }
            }
        }
    """

    def test_success(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label1 = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        label2 = label_factory(
            organization=org_with_owner, name="Feature", created_by=verified_user
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label1.id), str(label2.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        labels = data["data"]["addLabelsToTask"]["task"]["labels"]
        assert len(labels) == 2
        label_names = {lb["name"] for lb in labels}
        assert label_names == {"Bug", "Feature"}

    def test_other_org_label_rejected(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
        organization_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        other_org = organization_factory()
        other_label = label_factory(
            organization=other_org, name="Other", created_by=verified_user
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(other_label.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"]

    def test_already_assigned_ignored(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        task.labels.add(label)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        labels = data["data"]["addLabelsToTask"]["task"]["labels"]
        assert len(labels) == 1

    def test_nonexistent_label_rejected(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": ["999999"],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            data["errors"][0]["message"] == "존재하지 않는 Label이 포함되어 있습니다."
        )

    def test_non_member_cannot_add(
        self,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
        user_factory,
        verified_user,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"]

    def test_unauthenticated(
        self,
        api_client,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
        verified_user,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── TestRemoveLabelsFromTask ──


@pytest.mark.django_db
class TestRemoveLabelsFromTask:
    QUERY = """
        mutation RemoveLabelsFromTask($input: RemoveLabelsFromTaskInput!) {
            removeLabelsFromTask(input: $input) {
                task {
                    id
                    labels {
                        id
                        name
                    }
                }
            }
        }
    """

    def test_success(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label1 = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        label2 = label_factory(
            organization=org_with_owner, name="Feature", created_by=verified_user
        )
        task.labels.add(label1, label2)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label1.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        labels = data["data"]["removeLabelsFromTask"]["task"]["labels"]
        assert len(labels) == 1
        assert labels[0]["name"] == "Feature"

    def test_unassigned_label_ignored(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        labels = data["data"]["removeLabelsFromTask"]["task"]["labels"]
        assert len(labels) == 0

    def test_non_member_cannot_remove(
        self,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
        user_factory,
        verified_user,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        task.labels.add(label)
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"]

    def test_unauthenticated(
        self,
        api_client,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        label_factory,
        verified_user,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        label = label_factory(
            organization=org_with_owner, name="Bug", created_by=verified_user
        )
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "labelIds": [str(label.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."
