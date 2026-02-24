import pytest

from comments.models import Comment


@pytest.mark.django_db
class TestCommentModel:
    def test_default_content(self, comment_factory, task_factory):
        task = task_factory()
        comment = comment_factory(task=task, content="Hello")
        assert comment.content == "Hello"

    def test_parent_nullable(self, comment_factory, task_factory):
        task = task_factory()
        comment = comment_factory(task=task, parent=None)
        assert comment.parent is None

    def test_reply_relationship(self, comment_factory, task_factory):
        task = task_factory()
        parent = comment_factory(task=task)
        reply = comment_factory(task=task, parent=parent)
        assert reply.parent == parent
        assert parent.replies.first() == reply

    def test_task_cascade_delete(self, comment_factory, task_factory):
        task = task_factory()
        task_id = task.pk
        comment_factory(task=task)
        comment_factory(task=task)
        assert Comment.objects.filter(task_id=task_id).count() == 2
        task.delete()
        assert Comment.objects.filter(task_id=task_id).count() == 0

    def test_parent_cascade_delete(self, comment_factory, task_factory):
        task = task_factory()
        parent = comment_factory(task=task)
        parent_id = parent.pk
        comment_factory(task=task, parent=parent)
        comment_factory(task=task, parent=parent)
        assert Comment.objects.filter(parent_id=parent_id).count() == 2
        parent.delete()
        assert Comment.objects.filter(parent_id=parent_id).count() == 0

    def test_author_set_null_on_delete(
        self, comment_factory, task_factory, user_factory
    ):
        task = task_factory()
        author = user_factory(email_verified=True)
        comment = comment_factory(task=task, author=author)
        author.delete()
        comment.refresh_from_db()
        assert comment.author is None

    def test_ordering_by_created_at(self, comment_factory, task_factory):
        task = task_factory()
        c1 = comment_factory(task=task)
        c2 = comment_factory(task=task)
        c3 = comment_factory(task=task)
        result = list(Comment.objects.filter(task=task))
        assert result == [c1, c2, c3]

    def test_str(self, comment_factory, task_factory):
        task = task_factory()
        comment = comment_factory(task=task, content="Short comment")
        assert str(comment) == "Short comment"

    def test_str_truncated(self, comment_factory, task_factory):
        task = task_factory()
        long_content = "a" * 100
        comment = comment_factory(task=task, content=long_content)
        assert str(comment) == "a" * 50 + "..."

    def test_timestamps(self, comment_factory, task_factory):
        task = task_factory()
        comment = comment_factory(task=task)
        assert comment.created_at is not None
        assert comment.updated_at is not None
