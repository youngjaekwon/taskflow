import factory

from labels.models import Label


class LabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Label

    name = factory.Sequence(lambda n: f"Label {n}")
    color = "#808080"
    organization = factory.SubFactory(
        "organizations.tests.factories.OrganizationFactory"
    )
    created_by = factory.SubFactory(
        "users.tests.factories.UserFactory", email_verified=True
    )
