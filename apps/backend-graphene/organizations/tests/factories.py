import factory
from django.contrib.auth import get_user_model

from organizations.models import Organization, OrganizationMembership, Role

User = get_user_model()


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Organization {n}")
    description = ""
    created_by = factory.SubFactory(
        "users.tests.factories.UserFactory", email_verified=True
    )


class OrganizationMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizationMembership

    organization = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(
        "users.tests.factories.UserFactory", email_verified=True
    )
    role = Role.MEMBER
