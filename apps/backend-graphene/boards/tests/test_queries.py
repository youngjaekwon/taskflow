import json

import pytest
from django.urls import reverse

from conftest import make_auth_client

GRAPHQL_URL = reverse("graphql")


# ── board(id) ──


@pytest.mark.django_db
class TestBoardDetailQuery:
    QUERY = """
        query Board($id: ID!) {
            board(id: $id) {
                id
                name
                slug
                description
                project {
                    id
                }
                taskGroups {
                    id
                    name
                    position
                }
                createdBy {
                    id
                }
            }
        }
    """

    def test_project_member_can_view(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(board.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        board_data = data["data"]["board"]
        assert board_data["name"] == board.name
        assert board_data["slug"] == board.slug

    def test_org_admin_can_view(self, admin_user, org_with_admin, project_factory):
        project = project_factory(organization=org_with_admin)
        board = project.boards.first()
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(board.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["board"]["name"] == board.name

    def test_task_groups_ordered_by_position(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(board.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        task_groups = data["data"]["board"]["taskGroups"]
        positions = [tg["position"] for tg in task_groups]
        assert positions == sorted(positions)

    def test_org_member_without_project_membership_cannot_view(
        self, member_user, org_with_member, project_factory
    ):
        project = project_factory(organization=org_with_member)
        board = project.boards.first()
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(board.id)},
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
        board = project.boards.first()
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(board.id)},
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
        board = project.boards.first()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(board.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_nonexistent_board(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
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
        assert data["errors"][0]["message"] == "Board를 찾을 수 없습니다."


# ── boards(projectId) ──


@pytest.mark.django_db
class TestBoardListQuery:
    QUERY = """
        query Boards($projectId: ID!) {
            boards(projectId: $projectId) {
                id
                name
                slug
            }
        }
    """

    def test_project_member_can_list(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"projectId": str(project_with_member.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        boards = data["data"]["boards"]
        assert len(boards) >= 1

    def test_non_org_member_cannot_list(
        self, org_with_owner, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_owner)
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"projectId": str(project.id)},
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
                    "query": self.QUERY,
                    "variables": {"projectId": str(project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."
