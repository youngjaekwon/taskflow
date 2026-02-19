import pytest
from pytest_factoryboy import register

from organizations.models import OrganizationMembership, Role
from organizations.tests.factories import (
    OrganizationFactory,
    OrganizationMembershipFactory,
)

register(OrganizationFactory)
register(OrganizationMembershipFactory)


@pytest.fixture
def org_with_owner(organization_factory, verified_user):
    org = organization_factory(created_by=verified_user)
    OrganizationMembership.objects.create(
        organization=org, user=verified_user, role=Role.OWNER
    )
    return org


@pytest.fixture
def admin_user(user_factory):
    return user_factory(email_verified=True)


@pytest.fixture
def member_user(user_factory):
    return user_factory(email_verified=True)
