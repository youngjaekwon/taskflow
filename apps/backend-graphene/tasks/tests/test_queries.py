import json
from datetime import date

import pytest
from django.urls import reverse

from conftest import make_auth_client

GRAPHQL_URL = reverse("graphql")


# ── TestTaskDetail ──


@pytest.mark.django_db
class TestTaskDetail:
    QUERY = """
        query Task($id: ID!) {
            task(id: $id) {
                id
                title
                description
                status
                priority
                position
                dueDate
                assignee {
                    id
                }
                taskGroup {
                    id
                }
                createdBy {
                    id
                }
                createdAt
                updatedAt
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
    ):
        task = task_factory(task_group=task_group_in_project, created_by=verified_user)
        response = auth_client.post(
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
        task_data = data["data"]["task"]
        assert task_data["title"] == task.title
        assert task_data["status"] == "TODO"
        assert task_data["priority"] == "MEDIUM"
        assert task_data["createdBy"]["id"] == str(verified_user.id)
        assert task_data["taskGroup"]["id"] == str(task_group_in_project.id)

    def test_non_org_member_cannot_view(
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
                    "variables": {"id": str(task.id)},
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
                    "variables": {"id": "999999"},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["errors"][0]["message"] == "Task를 찾을 수 없습니다."


# ── TestTaskList ──


@pytest.mark.django_db
class TestTaskList:
    QUERY = """
        query Tasks(
            $projectId: ID!
            $filter: TaskFilterInput
            $pagination: PaginationInput
        ) {
            tasks(projectId: $projectId, filter: $filter, pagination: $pagination) {
                tasks {
                    id
                    title
                    status
                    priority
                    assignee {
                        id
                    }
                    dueDate
                }
                totalCount
                hasNext
                hasPrevious
            }
        }
    """

    def test_list_all(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task_factory(task_group=task_group_in_project, created_by=verified_user)
        task_factory(task_group=task_group_in_project, created_by=verified_user)
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
        result = data["data"]["tasks"]
        assert result["totalCount"] == 2
        assert len(result["tasks"]) == 2

    def test_filter_by_status(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            status="todo",
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            status="in_progress",
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            status="done",
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "filter": {"status": ["TODO", "IN_PROGRESS"]},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["tasks"]
        assert result["totalCount"] == 2

    def test_filter_by_priority(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            priority="low",
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            priority="high",
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            priority="urgent",
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "filter": {"priority": ["HIGH", "URGENT"]},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["tasks"]["totalCount"] == 2

    def test_filter_by_assignee(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            assignee=verified_user,
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            assignee=None,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "filter": {"assigneeId": str(verified_user.id)},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["tasks"]["totalCount"] == 1

    def test_filter_by_due_date_range(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            due_date=date(2026, 3, 1),
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            due_date=date(2026, 3, 15),
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            due_date=date(2026, 4, 1),
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "filter": {
                            "dueDateFrom": "2026-03-01",
                            "dueDateTo": "2026-03-31",
                        },
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["tasks"]["totalCount"] == 2

    def test_filter_by_search(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            title="Login feature",
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            title="Dashboard",
            description="login page link",
        )
        task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
            title="Settings",
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "filter": {"search": "login"},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["tasks"]["totalCount"] == 2


# ── TestTaskPagination ──


@pytest.mark.django_db
class TestTaskPagination:
    QUERY = """
        query Tasks(
            $projectId: ID!
            $filter: TaskFilterInput
            $pagination: PaginationInput
        ) {
            tasks(projectId: $projectId, filter: $filter, pagination: $pagination) {
                tasks {
                    id
                    title
                    status
                    priority
                    assignee {
                        id
                    }
                    dueDate
                }
                totalCount
                hasNext
                hasPrevious
            }
        }
    """

    def test_pagination(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        for i in range(15):
            task_factory(
                task_group=task_group_in_project,
                created_by=verified_user,
                position=i,
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "pagination": {"limit": 10, "offset": 0},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["tasks"]
        assert len(result["tasks"]) == 10
        assert result["totalCount"] == 15
        assert result["hasNext"] is True
        assert result["hasPrevious"] is False

    def test_next_page(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        for i in range(25):
            task_factory(
                task_group=task_group_in_project,
                created_by=verified_user,
                position=i,
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "pagination": {"limit": 10, "offset": 10},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["tasks"]
        assert len(result["tasks"]) == 10
        assert result["totalCount"] == 25
        assert result["hasNext"] is True
        assert result["hasPrevious"] is True

    def test_default_pagination(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        for i in range(5):
            task_factory(
                task_group=task_group_in_project,
                created_by=verified_user,
                position=i,
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["tasks"]
        assert len(result["tasks"]) == 5
        assert result["totalCount"] == 5
        assert result["hasNext"] is False
        assert result["hasPrevious"] is False

    def test_negative_limit_clamped_to_one(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        for i in range(3):
            task_factory(
                task_group=task_group_in_project,
                created_by=verified_user,
                position=i,
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "pagination": {"limit": -5, "offset": 0},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["tasks"]
        assert len(result["tasks"]) == 1

    def test_negative_offset_clamped_to_zero(
        self,
        auth_client,
        verified_user,
        org_with_owner,
        project_with_member,
        task_group_in_project,
        task_factory,
    ):
        for i in range(3):
            task_factory(
                task_group=task_group_in_project,
                created_by=verified_user,
                position=i,
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "projectId": str(project_with_member.id),
                        "pagination": {"limit": 10, "offset": -3},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["tasks"]
        assert len(result["tasks"]) == 3
        assert result["hasPrevious"] is False
