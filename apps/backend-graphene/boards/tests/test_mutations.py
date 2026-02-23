import json

import pytest
from django.urls import reverse

from boards.models import Board, TaskGroup
from conftest import make_auth_client

GRAPHQL_URL = reverse("graphql")

CREATE_BOARD = """
    mutation CreateBoard($input: CreateBoardInput!) {
        createBoard(input: $input) {
            board {
                id
                name
                slug
                description
                project {
                    id
                }
                createdBy {
                    id
                }
            }
        }
    }
"""

UPDATE_BOARD = """
    mutation UpdateBoard($input: UpdateBoardInput!) {
        updateBoard(input: $input) {
            board {
                id
                name
                slug
                description
            }
        }
    }
"""

DELETE_BOARD = """
    mutation DeleteBoard($id: ID!) {
        deleteBoard(id: $id) {
            success
        }
    }
"""


# ── CreateBoard ──


@pytest.mark.django_db
class TestCreateBoard:
    def test_success(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_BOARD,
                    "variables": {
                        "input": {
                            "projectId": str(project_with_member.id),
                            "name": "Sprint Board",
                            "description": "Sprint planning board",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        board_data = data["data"]["createBoard"]["board"]
        assert board_data["name"] == "Sprint Board"
        assert board_data["slug"] == "sprint-board"
        assert board_data["description"] == "Sprint planning board"
        assert board_data["createdBy"]["id"] == str(verified_user.id)

    def test_slug_duplicate_handling(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        # "Main Board"는 signal로 이미 생성되어 있음
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_BOARD,
                    "variables": {
                        "input": {
                            "projectId": str(project_with_member.id),
                            "name": "Main Board",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        board_data = data["data"]["createBoard"]["board"]
        assert board_data["slug"] == "main-board-2"

    def test_member_cannot_create(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_BOARD,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "name": "Test",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_non_org_member_cannot_create(
        self, org_with_owner, project_factory, user_factory
    ):
        project = project_factory(organization=org_with_owner)
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_BOARD,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "name": "Test",
                        }
                    },
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
                    "query": CREATE_BOARD,
                    "variables": {
                        "input": {
                            "projectId": str(project.id),
                            "name": "Test",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_empty_name_validation(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": CREATE_BOARD,
                    "variables": {
                        "input": {
                            "projectId": str(project_with_member.id),
                            "name": "",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"] is not None


# ── UpdateBoard ──


@pytest.mark.django_db
class TestUpdateBoard:
    def test_success(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_BOARD,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "name": "Updated Board",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        board_data = data["data"]["updateBoard"]["board"]
        assert board_data["name"] == "Updated Board"
        assert board_data["slug"] == "updated-board"

    def test_member_cannot_update(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        board = project.boards.first()
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_BOARD,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "name": "Hacked",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_unauthenticated(self, api_client, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(organization=org)
        board = project.boards.first()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": UPDATE_BOARD,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "name": "Hacked",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."


# ── DeleteBoard ──


@pytest.mark.django_db
class TestDeleteBoard:
    def test_success_with_cascade(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        board_id = board.id
        assert TaskGroup.objects.filter(board_id=board_id).count() == 4
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_BOARD,
                    "variables": {"id": str(board_id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteBoard"]["success"] is True
        assert not Board.objects.filter(pk=board_id).exists()
        assert TaskGroup.objects.filter(board_id=board_id).count() == 0

    def test_member_cannot_delete(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        board = project.boards.first()
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": DELETE_BOARD,
                    "variables": {"id": str(board.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "권한이 부족합니다."

    def test_non_org_member_cannot_delete(
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
                    "query": DELETE_BOARD,
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
                    "query": DELETE_BOARD,
                    "variables": {"id": str(board.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."
