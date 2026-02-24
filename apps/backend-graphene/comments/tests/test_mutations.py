import json

import pytest
from django.urls import reverse

from comments.models import Comment
from conftest import make_auth_client
from organizations.models import OrganizationMembership, Role

GRAPHQL_URL = reverse("graphql")


# ── TestCreateComment ──


@pytest.mark.django_db
class TestCreateComment:
    QUERY = """
        mutation CreateComment($input: CreateCommentInput!) {
            createComment(input: $input) {
                comment {
                    id
                    content
                    task { id }
                    parent { id }
                    author { id }
                }
            }
        }
    """

    def test_success(self, auth_client, verified_user, task_in_project):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "First comment",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["createComment"]["comment"]
        assert result["content"] == "First comment"
        assert result["author"]["id"] == str(verified_user.id)
        assert result["parent"] is None

    def test_reply_success(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        parent = comment_factory(task=task_in_project, author=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "Reply comment",
                            "parentId": str(parent.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        comment = data["data"]["createComment"]["comment"]
        assert comment["content"] == "Reply comment"
        assert comment["parent"]["id"] == str(parent.id)

    def test_nested_reply_rejected(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        parent = comment_factory(task=task_in_project, author=verified_user)
        reply = comment_factory(
            task=task_in_project,
            author=verified_user,
            parent=parent,
        )
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "Nested reply",
                            "parentId": str(reply.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createComment"] is None
        assert "1단계 대댓글만" in data["errors"][0]["message"]

    def test_nonexistent_parent_id(self, auth_client, task_in_project):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "Reply",
                            "parentId": "99999",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createComment"] is None
        assert "부모 댓글을 찾을 수 없습니다" in data["errors"][0]["message"]

    def test_parent_from_different_task(
        self,
        auth_client,
        task_in_project,
        task_factory,
        comment_factory,
        verified_user,
        task_group_in_project,
    ):
        other_task = task_factory(
            task_group=task_group_in_project,
            created_by=verified_user,
        )
        parent = comment_factory(task=other_task, author=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "Reply",
                            "parentId": str(parent.id),
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createComment"] is None
        assert "같은 Task" in data["errors"][0]["message"]

    def test_empty_content(self, auth_client, task_in_project):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createComment"] is None
        assert data["errors"]

    def test_nonexistent_task(self, auth_client):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": "99999",
                            "content": "Hello",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createComment"] is None
        assert "Task를 찾을 수 없습니다" in data["errors"][0]["message"]

    def test_no_permission(self, task_in_project, user_factory):
        outsider = user_factory(email_verified=True)
        client = make_auth_client(outsider)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "Hello",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createComment"] is None
        assert data["errors"]

    def test_unauthenticated(self, api_client, task_in_project):
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "taskId": str(task_in_project.id),
                            "content": "Hello",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createComment"] is None
        assert "로그인이 필요합니다" in data["errors"][0]["message"]


# ── TestUpdateComment ──


@pytest.mark.django_db
class TestUpdateComment:
    QUERY = """
        mutation UpdateComment($input: UpdateCommentInput!) {
            updateComment(input: $input) {
                comment {
                    id
                    content
                }
            }
        }
    """

    def test_success(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        comment = comment_factory(task=task_in_project, author=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "commentId": str(comment.id),
                            "content": "Updated content",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        result = data["data"]["updateComment"]["comment"]
        assert result["content"] == "Updated content"

    def test_nonexistent_comment(self, auth_client):
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "commentId": "99999",
                            "content": "Updated",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateComment"] is None
        assert "Comment를 찾을 수 없습니다" in data["errors"][0]["message"]

    def test_non_author_rejected(
        self,
        task_in_project,
        comment_factory,
        verified_user,
        user_factory,
        org_with_owner,
    ):
        comment = comment_factory(task=task_in_project, author=verified_user)
        other_user = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org_with_owner,
            user=other_user,
            role=Role.ADMIN,
        )
        client = make_auth_client(other_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "commentId": str(comment.id),
                            "content": "Hacked",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateComment"] is None
        assert "작성자만" in data["errors"][0]["message"]

    def test_empty_content(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        comment = comment_factory(task=task_in_project, author=verified_user)
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "commentId": str(comment.id),
                            "content": "",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateComment"] is None
        assert data["errors"]

    def test_unauthenticated(
        self, api_client, task_in_project, comment_factory, verified_user
    ):
        comment = comment_factory(task=task_in_project, author=verified_user)
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {
                        "input": {
                            "commentId": str(comment.id),
                            "content": "Updated",
                        }
                    },
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateComment"] is None
        assert "로그인이 필요합니다" in data["errors"][0]["message"]


# ── TestDeleteComment ──


@pytest.mark.django_db
class TestDeleteComment:
    QUERY = """
        mutation DeleteComment($id: ID!) {
            deleteComment(id: $id) {
                success
            }
        }
    """

    def test_success(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        comment = comment_factory(task=task_in_project, author=verified_user)
        comment_id = comment.id
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(comment_id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteComment"]["success"] is True
        assert not Comment.objects.filter(pk=comment_id).exists()

    def test_cascade_delete_replies(
        self, auth_client, task_in_project, comment_factory, verified_user
    ):
        parent = comment_factory(task=task_in_project, author=verified_user)
        reply1 = comment_factory(
            task=task_in_project,
            author=verified_user,
            parent=parent,
        )
        reply2 = comment_factory(
            task=task_in_project,
            author=verified_user,
            parent=parent,
        )
        parent_id = parent.id
        response = auth_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(parent_id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteComment"]["success"] is True
        assert not Comment.objects.filter(pk=parent_id).exists()
        assert not Comment.objects.filter(pk=reply1.id).exists()
        assert not Comment.objects.filter(pk=reply2.id).exists()

    def test_non_author_rejected(
        self,
        task_in_project,
        comment_factory,
        verified_user,
        user_factory,
        org_with_owner,
    ):
        comment = comment_factory(task=task_in_project, author=verified_user)
        other_user = user_factory(email_verified=True)
        OrganizationMembership.objects.create(
            organization=org_with_owner,
            user=other_user,
            role=Role.ADMIN,
        )
        client = make_auth_client(other_user)
        response = client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(comment.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteComment"] is None
        assert "작성자만" in data["errors"][0]["message"]

    def test_unauthenticated(
        self, api_client, task_in_project, comment_factory, verified_user
    ):
        comment = comment_factory(task=task_in_project, author=verified_user)
        response = api_client.post(
            GRAPHQL_URL,
            json.dumps(
                {
                    "query": self.QUERY,
                    "variables": {"id": str(comment.id)},
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteComment"] is None
        assert "로그인이 필요합니다" in data["errors"][0]["message"]
