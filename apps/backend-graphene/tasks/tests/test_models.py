import pytest

from tasks.models import Task, TaskPriority, TaskStatus


@pytest.mark.django_db
class TestTaskModel:
    def test_default_status(self, task_factory, task_group_factory):
        tg = task_group_factory()
        task = task_factory(task_group=tg)
        assert task.status == TaskStatus.TODO

    def test_default_priority(self, task_factory, task_group_factory):
        tg = task_group_factory()
        task = task_factory(task_group=tg)
        assert task.priority == TaskPriority.MEDIUM

    def test_default_description(self, task_factory, task_group_factory):
        tg = task_group_factory()
        task = task_factory(task_group=tg)
        assert task.description == ""

    def test_default_position(self, task_factory, task_group_factory):
        tg = task_group_factory()
        task = task_factory(task_group=tg)
        assert task.position == 0

    def test_assignee_nullable(self, task_factory, task_group_factory):
        tg = task_group_factory()
        task = task_factory(task_group=tg, assignee=None)
        assert task.assignee is None

    def test_due_date_nullable(self, task_factory, task_group_factory):
        tg = task_group_factory()
        task = task_factory(task_group=tg, due_date=None)
        assert task.due_date is None

    def test_ordering_by_position(self, task_factory, task_group_factory):
        tg = task_group_factory()
        t3 = task_factory(task_group=tg, position=2)
        t1 = task_factory(task_group=tg, position=0)
        t2 = task_factory(task_group=tg, position=1)
        result = list(Task.objects.filter(task_group=tg))
        assert result == [t1, t2, t3]

    def test_cascade_delete_with_task_group(self, task_factory, task_group_factory):
        tg = task_group_factory()
        tg_id = tg.pk
        task_factory(task_group=tg)
        task_factory(task_group=tg)
        assert Task.objects.filter(task_group_id=tg_id).count() == 2
        tg.delete()
        assert Task.objects.filter(task_group_id=tg_id).count() == 0

    def test_assignee_set_null_on_delete(
        self, task_factory, task_group_factory, user_factory
    ):
        tg = task_group_factory()
        assignee = user_factory(email_verified=True)
        task = task_factory(task_group=tg, assignee=assignee)
        assignee.delete()
        task.refresh_from_db()
        assert task.assignee is None

    def test_created_by_set_null_on_delete(
        self, task_factory, task_group_factory, user_factory
    ):
        tg = task_group_factory()
        creator = user_factory(email_verified=True)
        task = task_factory(task_group=tg, created_by=creator)
        creator.delete()
        task.refresh_from_db()
        assert task.created_by is None

    def test_str(self, task_factory, task_group_factory):
        tg = task_group_factory()
        task = task_factory(title="My Task", task_group=tg)
        assert str(task) == "My Task"
