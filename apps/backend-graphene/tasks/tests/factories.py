import factory

from tasks.models import Task


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    description = ""
    task_group = factory.SubFactory("boards.tests.factories.TaskGroupFactory")
    created_by = factory.SubFactory(
        "users.tests.factories.UserFactory", email_verified=True
    )
