import factory

from boards.models import Board, TaskGroup


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Board

    name = factory.Sequence(lambda n: f"Board {n}")
    description = ""
    project = factory.SubFactory("projects.tests.factories.ProjectFactory")
    created_by = factory.SubFactory(
        "users.tests.factories.UserFactory", email_verified=True
    )


class TaskGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskGroup

    name = factory.Sequence(lambda n: f"TaskGroup {n}")
    board = factory.SubFactory(BoardFactory)
