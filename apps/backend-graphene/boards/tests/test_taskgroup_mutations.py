import json

import pytest
from django.urls import reverse

from boards.models import TaskGroup
from conftest import make_auth_client
from tasks.tests.factories import TaskFactory

GRAPHQL_URL = reverse("graphql")


# ── CreateTaskGroup ──


@pytest.mark.django_db
class TestCreateTaskGroup:
    QUERY = """
        mutation CreateTaskGroup($input: CreateTaskGroupInput!) {
            createTaskGroup(input: $input) {
                taskGroup {
                    id
                    name
                    position
                }
            }
        }
    """

    def test_success_auto_position(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        # 기본 4개 TaskGroup이 있으므로 다음 position은 4
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "name": "Backlog",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        tg_data = data["data"]["createTaskGroup"]["taskGroup"]
        assert tg_data["name"] == "Backlog"
        assert tg_data["position"] == 4

    def test_empty_board_position_zero(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        board_factory,
    ):
        board = board_factory(project=project_with_member, created_by=verified_user)
        # signal로 생성된 TaskGroup 없는 새 Board
        TaskGroup.objects.filter(board=board).delete()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "name": "First Group",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        tg_data = data["data"]["createTaskGroup"]["taskGroup"]
        assert tg_data["position"] == 0

    def test_member_cannot_create(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        board = project.boards.first()
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
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

    def test_unauthenticated(self, api_client, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(organization=org)
        board = project.boards.first()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
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


# ── UpdateTaskGroup ──


@pytest.mark.django_db
class TestUpdateTaskGroup:
    QUERY = """
        mutation UpdateTaskGroup($input: UpdateTaskGroupInput!) {
            updateTaskGroup(input: $input) {
                taskGroup {
                    id
                    name
                }
            }
        }
    """

    def test_success(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        tg = board.task_groups.first()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(tg.id),
                            "name": "Renamed Group",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        tg_data = data["data"]["updateTaskGroup"]["taskGroup"]
        assert tg_data["name"] == "Renamed Group"

    def test_nonexistent_task_group_id(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": "999999",
                            "name": "Ghost",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "TaskGroup을 찾을 수 없습니다."

    def test_other_board_task_group(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        board_factory,
        task_group_factory,
    ):
        board = project_with_member.boards.first()
        other_board = board_factory(
            project=project_with_member, created_by=verified_user
        )
        other_tg = task_group_factory(board=other_board)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(other_tg.id),
                            "name": "Stolen",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "TaskGroup을 찾을 수 없습니다."

    def test_member_cannot_update(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        board = project.boards.first()
        tg = board.task_groups.first()
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(tg.id),
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
        tg = board.task_groups.first()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(tg.id),
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


# ── DeleteTaskGroup ──


@pytest.mark.django_db
class TestDeleteTaskGroup:
    QUERY = """
        mutation DeleteTaskGroup($input: DeleteTaskGroupInput!) {
            deleteTaskGroup(input: $input) {
                success
            }
        }
    """

    def test_success(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        tg = board.task_groups.first()
        tg_id = tg.id
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(tg_id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteTaskGroup"]["success"] is True
        assert not TaskGroup.objects.filter(pk=tg_id).exists()

    def test_nonexistent_task_group_id(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": "999999",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "TaskGroup을 찾을 수 없습니다."

    def test_other_board_task_group(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        board_factory,
        task_group_factory,
    ):
        board = project_with_member.boards.first()
        other_board = board_factory(
            project=project_with_member, created_by=verified_user
        )
        other_tg = task_group_factory(board=other_board)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(other_tg.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "TaskGroup을 찾을 수 없습니다."

    def test_member_cannot_delete(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        board = project.boards.first()
        tg = board.task_groups.first()
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(tg.id),
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
        tg = board.task_groups.first()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(tg.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_blocked_by_existing_tasks(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
    ):
        board = project_with_member.boards.first()
        tg = board.task_groups.first()
        TaskFactory(task_group=tg, created_by=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupId": str(tg.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        err_msg = data["errors"][0]["message"]
        assert "Task가 존재하는 TaskGroup은 삭제할 수 없습니다" in err_msg
        assert TaskGroup.objects.filter(pk=tg.id).exists()


# ── ReorderTaskGroups ──


@pytest.mark.django_db
class TestReorderTaskGroups:
    QUERY = """
        mutation ReorderTaskGroups($input: ReorderTaskGroupsInput!) {
            reorderTaskGroups(input: $input) {
                taskGroups {
                    id
                    name
                    position
                }
            }
        }
    """

    def test_success(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        tgs = list(board.task_groups.all())
        # 역순으로 재정렬
        reversed_ids = [str(tg.id) for tg in reversed(tgs)]
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupIds": reversed_ids,
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["reorderTaskGroups"]["taskGroups"]
        for i, tg in enumerate(result):
            assert tg["position"] == i
        # 첫번째 결과가 원래 마지막이었던 항목
        assert result[0]["name"] == tgs[-1].name

    def test_incomplete_id_list(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        tgs = list(board.task_groups.all())
        # 하나만 전달
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupIds": [str(tgs[0].id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        err_msg = data["errors"][0]["message"]
        assert "이 Board의 모든 TaskGroup ID를 빠짐없이 전달해야 합니다." in err_msg

    def test_other_board_id(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        board_factory,
    ):
        board = project_with_member.boards.first()
        other_board = board_factory(
            project=project_with_member, created_by=verified_user
        )
        other_tgs = list(other_board.task_groups.all())
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupIds": [str(tg.id) for tg in other_tgs],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"] is not None

    def test_duplicate_ids(
        self, auth_client, verified_user, org_with_owner, project_with_member
    ):
        board = project_with_member.boards.first()
        tgs = list(board.task_groups.all())
        # 첫 번째 ID를 중복으로 전달
        duplicate_ids = [str(tgs[0].id), str(tgs[0].id)] + [
            str(tg.id) for tg in tgs[1:]
        ]
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupIds": duplicate_ids,
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            data["errors"][0]["message"] == "중복된 TaskGroup ID가 포함되어 있습니다."
        )

    def test_member_cannot_reorder(self, member_user, org_with_member, project_factory):
        project = project_factory(organization=org_with_member)
        board = project.boards.first()
        tgs = list(board.task_groups.all())
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupIds": [str(tg.id) for tg in tgs],
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
        tgs = list(board.task_groups.all())
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "boardId": str(board.id),
                            "taskGroupIds": [str(tg.id) for tg in tgs],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."
