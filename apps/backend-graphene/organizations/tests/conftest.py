import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from organizations.models import OrganizationMembership, Role
from organizations.tests.factories import (
    OrganizationFactory,
    OrganizationMembershipFactory,
)
from users.tests.factories import UserFactory

register(UserFactory)
register(OrganizationFactory)
register(OrganizationMembershipFactory)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_user(user_factory):
    return user_factory(email_verified=True)


@pytest.fixture
def auth_client(api_client, verified_user):
    refresh = RefreshToken.for_user(verified_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


def make_auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


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
