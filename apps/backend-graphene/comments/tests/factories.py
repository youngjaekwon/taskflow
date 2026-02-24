import factory

from comments.models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Sequence(lambda n: f"Comment {n}")
    task = factory.SubFactory("tasks.tests.factories.TaskFactory")
    author = factory.SubFactory(
        "users.tests.factories.UserFactory", email_verified=True
    )
