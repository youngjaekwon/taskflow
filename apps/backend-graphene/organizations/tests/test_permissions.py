import pytest

from organizations.decorators import check_role, get_membership
from organizations.models import OrganizationMembership, Role


@pytest.mark.django_db
class TestGetMembership:
    def test_returns_membership_when_exists(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.MEMBER
        )
        membership = get_membership(user, org.id)
        assert membership is not None
        assert membership.role == Role.MEMBER

    def test_returns_none_when_not_member(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        assert get_membership(user, org.id) is None


@pytest.mark.django_db
class TestCheckRole:
    def test_owner_passes_all_roles(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        membership = OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.OWNER
        )
        assert check_role(membership, Role.MEMBER) is True
        assert check_role(membership, Role.ADMIN) is True
        assert check_role(membership, Role.OWNER) is True

    def test_admin_passes_admin_and_member(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        membership = OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.ADMIN
        )
        assert check_role(membership, Role.MEMBER) is True
        assert check_role(membership, Role.ADMIN) is True
        assert check_role(membership, Role.OWNER) is False

    def test_member_passes_member_only(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        membership = OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.MEMBER
        )
        assert check_role(membership, Role.MEMBER) is True
        assert check_role(membership, Role.ADMIN) is False
        assert check_role(membership, Role.OWNER) is False
