import factory

from projects.models import Project, ProjectMembership


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    description = ""
    organization = factory.SubFactory(
        "organizations.tests.factories.OrganizationFactory"
    )
    created_by = factory.SubFactory(
        "users.tests.factories.UserFactory", email_verified=True
    )


class ProjectMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectMembership

    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory("users.tests.factories.UserFactory", email_verified=True)
