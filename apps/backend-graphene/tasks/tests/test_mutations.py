import json

import pytest
from django.urls import reverse

from conftest import make_auth_client
from organizations.models import OrganizationMembership, Role
from projects.models import ProjectMembership
from tasks.models import Task

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


# ── TestCreateTask ──


@pytest.mark.django_db
class TestCreateTask:
    QUERY = """
        mutation CreateTask($input: CreateTaskInput!) {
            createTask(input: $input) {
                task {
                    id
                    title
                    description
                    status
                    priority
                    position
                    assignee {
                        id
                    }
                    taskGroup {
                        id
                    }
                    createdBy {
                        id
                    }
                }
            }
        }
    """

    def test_success(
        self, auth_client, verified_user, org_with_owner, task_group_in_project
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "title": "New Task",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        task_data = data["data"]["createTask"]["task"]
        assert task_data["title"] == "New Task"
        assert task_data["status"] == "TODO"
        assert task_data["priority"] == "MEDIUM"
        assert task_data["position"] == 0
        assert task_data["createdBy"]["id"] == str(verified_user.id)

    def test_with_assignee(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "title": "Assigned Task",
                            "assigneeId": str(verified_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        task_data = data["data"]["createTask"]["task"]
        assert task_data["assignee"]["id"] == str(verified_user.id)

    def test_non_project_member_assignee(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        task_group_in_project,
        user_factory,
    ):
        outsider = user_factory(email_verified=True)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "title": "Task",
                            "assigneeId": str(outsider.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "담당자는 프로젝트 멤버여야 합니다."

    def test_empty_title(
        self, auth_client, verified_user, org_with_owner, task_group_in_project
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "title": "",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"] is not None

    def test_non_org_member_cannot_create(
        self, org_with_owner, task_group_in_project, user_factory
    ):
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "title": "Task",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이 Organization의 멤버가 아닙니다."

    def test_unauthenticated(self, api_client, task_group_factory):
        tg = task_group_factory()
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(tg.id),
                            "title": "Task",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_position_auto_increment(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        task_group_in_project,
        task_factory,
    ):
        task_factory(task_group=task_group_in_project, position=0)
        task_factory(task_group=task_group_in_project, position=1)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "title": "Third Task",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createTask"]["task"]["position"] == 2


# ── TestUpdateTask ──


@pytest.mark.django_db
class TestUpdateTask:
    QUERY = """
        mutation UpdateTask($input: UpdateTaskInput!) {
            updateTask(input: $input) {
                task {
                    id
                    title
                    description
                    status
                    priority
                    dueDate
                }
            }
        }
    """

    def test_success_partial_update(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task = task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            title="Original",
            description="Original desc",
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "title": "Updated",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        task_data = data["data"]["updateTask"]["task"]
        assert task_data["title"] == "Updated"
        assert task_data["description"] == "Original desc"

    def test_status_change(
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
                            "status": "IN_PROGRESS",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateTask"]["task"]["status"] == "IN_PROGRESS"

    def test_non_org_member_cannot_update(
        self,
        org_with_owner,
        task_group_in_project,
        task_factory,
        verified_user,
        user_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
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
                            "title": "Hacked",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "이 Organization의 멤버가 아닙니다."

    def test_nonexistent_task(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
    ):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": "999999",
                            "title": "Not Found",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "Task를 찾을 수 없습니다."


# ── TestDeleteTask ──


@pytest.mark.django_db
class TestDeleteTask:
    QUERY = """
        mutation DeleteTask($id: ID!) {
            deleteTask(id: $id) {
                success
            }
        }
    """

    def test_creator_can_delete(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        task_id = task.id
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(task_id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteTask"]["success"] is True
        assert not Task.objects.filter(pk=task_id).exists()

    def test_admin_can_delete(
        self,
        admin_user,
        org_with_admin,
        project_with_member,
        task_group_in_project,
        task_factory,
        verified_user,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        client = make_auth_client(admin_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(task.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteTask"]["success"] is True

    def test_member_non_creator_cannot_delete(
        self,
        member_user,
        org_with_member,
        project_with_member,
        task_group_in_project,
        task_factory,
        verified_user,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        ProjectMembership.objects.create(
            project=project_with_member, user=member_user, added_by=verified_user
        )
        client = make_auth_client(member_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(task.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "Task 삭제 권한이 없습니다."

    def test_unauthenticated(
        self, api_client, task_group_factory, task_factory, user_factory
    ):
        creator = user_factory(email_verified=True)
        tg = task_group_factory()
        task = task_factory(task_group=tg, created_by=creator)
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(task.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "로그인이 필요합니다."

    def test_positions_adjusted_after_delete(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        t0 = task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            position=0,
        )
        t1 = task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            position=1,
        )
        t2 = task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            position=2,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(t1.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["deleteTask"]["success"] is True

        t0.refresh_from_db()
        t2.refresh_from_db()
        assert t0.position == 0
        assert t2.position == 1


# ── TestMoveTask ──


@pytest.mark.django_db
class TestMoveTask:
    QUERY = """
        mutation MoveTask($input: MoveTaskInput!) {
            moveTask(input: $input) {
                task {
                    id
                    taskGroup {
                        id
                    }
                    position
                }
            }
        }
    """

    def test_move_to_another_task_group(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        board = task_group_in_project.board
        target_tg = board.task_groups.exclude(pk=task_group_in_project.pk).first()
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "targetTaskGroupId": str(target_tg.id),
                            "position": 0,
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        task_data = data["data"]["moveTask"]["task"]
        assert task_data["taskGroup"]["id"] == str(target_tg.id)
        assert task_data["position"] == 0

    def test_move_without_position(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        board = task_group_in_project.board
        target_tg = board.task_groups.exclude(pk=task_group_in_project.pk).first()
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "targetTaskGroupId": str(target_tg.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["moveTask"]["task"]["taskGroup"]["id"] == str(target_tg.id)

    def test_move_to_different_board_rejected(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        board_factory,
        task_group_factory,
    ):
        other_board = board_factory(
            project=project_with_member, created_by=verified_user
        )
        other_tg = task_group_factory(board=other_board)
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "targetTaskGroupId": str(other_tg.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "같은 Board 내에서만 이동할 수 있습니다."


# ── TestReorderTasks ──


@pytest.mark.django_db
class TestReorderTasks:
    QUERY = """
        mutation ReorderTasks($input: ReorderTasksInput!) {
            reorderTasks(input: $input) {
                tasks {
                    id
                    position
                }
            }
        }
    """

    def test_reorder_success(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        t1 = task_factory(
            task_group=task_group_in_project, created_by=verified_user, position=0
        )
        t2 = task_factory(
            task_group=task_group_in_project, created_by=verified_user, position=1
        )
        t3 = task_factory(
            task_group=task_group_in_project, created_by=verified_user, position=2
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "taskIds": [str(t3.id), str(t1.id), str(t2.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        tasks = data["data"]["reorderTasks"]["tasks"]
        assert tasks[0]["id"] == str(t3.id)
        assert tasks[0]["position"] == 0
        assert tasks[1]["id"] == str(t1.id)
        assert tasks[1]["position"] == 1
        assert tasks[2]["id"] == str(t2.id)
        assert tasks[2]["position"] == 2

    def test_includes_task_from_other_group(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        board = task_group_in_project.board
        other_tg = board.task_groups.exclude(pk=task_group_in_project.pk).first()
        t1 = task_factory(
            task_group=task_group_in_project, created_by=verified_user, position=0
        )
        t_other = task_factory(
            task_group=other_tg, created_by=verified_user, position=0
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskGroupId": str(task_group_in_project.id),
                            "taskIds": [str(t1.id), str(t_other.id)],
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"] is not None


# ── TestAssignTask ──


@pytest.mark.django_db
class TestAssignTask:
    QUERY = """
        mutation AssignTask($input: AssignTaskInput!) {
            assignTask(input: $input) {
                task {
                    id
                    assignee {
                        id
                    }
                }
            }
        }
    """

    def test_assign_success(
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
                            "assigneeId": str(verified_user.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["assignTask"]["task"]["assignee"]["id"] == str(
            verified_user.id
        )

    def test_unassign(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task = task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            assignee=verified_user,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "assigneeId": None,
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["assignTask"]["task"]["assignee"] is None

    def test_non_project_member_assignee_rejected(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
        user_factory,
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        outsider = user_factory(email_verified=True)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task.id),
                            "assigneeId": str(outsider.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "담당자는 프로젝트 멤버여야 합니다."
