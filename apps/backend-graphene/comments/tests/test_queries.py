import json

import pytest
from django.urls import reverse

from conftest import make_auth_client

GRAPHQL_URL = reverse("graphql")


# ── TestCommentList ──


@pytest.mark.django_db
class TestCommentList:
    QUERY = """
        query Comments($taskId: ID!, $pagination: PaginationInput) {
            comments(taskId: $taskId, pagination: $pagination) {
                comments {
                    id
                    content
                    author { id }
                    parent { id }
                    replies {
                        id
                        content
                        author { id }
                    }
                    createdAt
                }
                totalCount
                hasNext
                hasPrevious
            }
        }
    """

    def test_list_top_level_with_replies(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        c1 = comment_factory(
            task=task_in_project,
            author=verified_user,
            content="Top 1",
        )
        comment_factory(
            task=task_in_project,
            author=verified_user,
            content="Top 2",
        )
        comment_factory(
            task=task_in_project,
            author=verified_user,
            content="Reply 1",
            parent=c1,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"taskId": str(task_in_project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["comments"]
        assert result["totalCount"] == 2
        assert len(result["comments"]) == 2
        # First comment should have replies
        first = result["comments"][0]
        assert first["content"] == "Top 1"
        assert len(first["replies"]) == 1
        assert first["replies"][0]["content"] == "Reply 1"
        # Second comment has no replies
        second = result["comments"][1]
        assert second["content"] == "Top 2"
        assert len(second["replies"]) == 0

    def test_ordering_by_created_at(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        comment_factory(
            task=task_in_project,
            author=verified_user,
            content="First",
        )
        comment_factory(
            task=task_in_project,
            author=verified_user,
            content="Second",
        )
        comment_factory(
            task=task_in_project,
            author=verified_user,
            content="Third",
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"taskId": str(task_in_project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        comments = data["data"]["comments"]["comments"]
        contents = [c["content"] for c in comments]
        assert contents == ["First", "Second", "Third"]

    def test_replies_ordering(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        parent = comment_factory(task=task_in_project, author=verified_user)
        comment_factory(
            task=task_in_project,
            author=verified_user,
            content="R1",
            parent=parent,
        )
        comment_factory(
            task=task_in_project,
            author=verified_user,
            content="R2",
            parent=parent,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"taskId": str(task_in_project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        replies = data["data"]["comments"]["comments"][0]["replies"]
        assert [r["content"] for r in replies] == ["R1", "R2"]

    def test_no_permission(self, task_in_project, user_factory):
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "taskId": str(task_in_project.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["comments"] is None
        assert data["errors"]

    def test_unauthenticated(self, api_client, task_in_project):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "taskId": str(task_in_project.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["comments"] is None
        assert "로그인이 필요합니다" in data["errors"][0]["message"]


# ── TestCommentPagination ──


@pytest.mark.django_db
class TestCommentPagination:
    QUERY = """
        query Comments($taskId: ID!, $pagination: PaginationInput) {
            comments(taskId: $taskId, pagination: $pagination) {
                comments {
                    id
                    content
                }
                totalCount
                hasNext
                hasPrevious
            }
        }
    """

    def test_pagination(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        for i in range(15):
            comment_factory(
                task=task_in_project,
                author=verified_user,
                content=f"Comment {i}",
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "taskId": str(task_in_project.id),
                        "pagination": {"limit": 10, "offset": 0},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["comments"]
        assert len(result["comments"]) == 10
        assert result["totalCount"] == 15
        assert result["hasNext"] is True
        assert result["hasPrevious"] is False

    def test_next_page(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        for i in range(25):
            comment_factory(
                task=task_in_project,
                author=verified_user,
                content=f"Comment {i}",
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "taskId": str(task_in_project.id),
                        "pagination": {"limit": 10, "offset": 10},
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["comments"]
        assert len(result["comments"]) == 10
        assert result["totalCount"] == 25
        assert result["hasNext"] is True
        assert result["hasPrevious"] is True

    def test_default_pagination(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        for i in range(5):
            comment_factory(
                task=task_in_project,
                author=verified_user,
                content=f"Comment {i}",
            )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "taskId": str(task_in_project.id),
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["comments"]
        assert len(result["comments"]) == 5
        assert result["totalCount"] == 5
        assert result["hasNext"] is False
        assert result["hasPrevious"] is False


# ── TestCommentCount ──


@pytest.mark.django_db
class TestCommentCount:
    QUERY = """
        query Task($id: ID!) {
            task(id: $id) {
                id
                title
                commentCount
            }
        }
    """

    def test_comment_count(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        comment_factory(task=task_in_project, author=verified_user)
        comment_factory(task=task_in_project, author=verified_user)
        parent = comment_factory(task=task_in_project, author=verified_user)
        comment_factory(
            task=task_in_project,
            author=verified_user,
            parent=parent,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(task_in_project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["task"]["commentCount"] == 4

    def test_comment_count_zero(self, auth_client, task_in_project):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(task_in_project.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["task"]["commentCount"] == 0
