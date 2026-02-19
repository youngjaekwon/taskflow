import pytest
from pytest_factoryboy import register

from organizations.models import OrganizationMembership, Role
from organizations.tests.factories import (
    OrganizationFactory,
    OrganizationMembershipFactory,
)
from projects.models import ProjectMembership
from projects.tests.factories import ProjectFactory, ProjectMembershipFactory

register(OrganizationFactory)
register(OrganizationMembershipFactory)
register(ProjectFactory)
register(ProjectMembershipFactory)


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


@pytest.fixture
def org_with_admin(org_with_owner, admin_user):
    OrganizationMembership.objects.create(
        organization=org_with_owner, user=admin_user, role=Role.ADMIN
    )
    return org_with_owner


@pytest.fixture
def org_with_member(org_with_owner, member_user):
    OrganizationMembership.objects.create(
        organization=org_with_owner, user=member_user, role=Role.MEMBER
    )
    return org_with_owner


@pytest.fixture
def project_with_member(project_factory, org_with_owner, verified_user):
    project = project_factory(organization=org_with_owner, created_by=verified_user)
    ProjectMembership.objects.create(
        project=project, user=verified_user, added_by=verified_user
    )
    return project
