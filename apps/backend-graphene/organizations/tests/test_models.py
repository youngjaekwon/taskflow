import pytest

from organizations.models import OrganizationMembership, Role


@pytest.mark.django_db
class TestOrganizationModel:
    def test_create_organization(self, organization_factory):
        org = organization_factory(name="Test Org")
        assert org.name == "Test Org"
        assert org.slug == "test-org"

    def test_slug_auto_generated_from_name(self, organization_factory):
        org = organization_factory(name="My Cool Organization")
        assert org.slug == "my-cool-organization"

    def test_slug_unique_with_suffix(self, organization_factory):
        org1 = organization_factory(name="Duplicate")
        org2 = organization_factory(name="Duplicate")
        assert org1.slug == "duplicate"
        assert org2.slug == "duplicate-2"

    def test_slug_unique_with_multiple_duplicates(self, organization_factory):
        org1 = organization_factory(name="Same")
        org2 = organization_factory(name="Same")
        org3 = organization_factory(name="Same")
        assert org1.slug == "same"
        assert org2.slug == "same-2"
        assert org3.slug == "same-3"

    def test_description_defaults_to_blank(self, organization_factory):
        org = organization_factory()
        assert org.description == ""

    def test_str_returns_name(self, organization_factory):
        org = organization_factory(name="Str Test")
        assert str(org) == "Str Test"

    def test_created_by_set_null_on_user_delete(
        self, organization_factory, user_factory
    ):
        user = user_factory()
        org = organization_factory(created_by=user)
        user.delete()
        org.refresh_from_db()
        assert org.created_by is None


@pytest.mark.django_db
class TestOrganizationMembershipModel:
    def test_create_membership(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        membership = OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.MEMBER
        )
        assert membership.role == Role.MEMBER
        assert membership.organization == org
        assert membership.user == user

    def test_unique_together_constraint(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.MEMBER
        )
        with pytest.raises(Exception):
            OrganizationMembership.objects.create(
                organization=org, user=user, role=Role.ADMIN
            )

    def test_default_role_is_member(self, organization_factory, user_factory):
        org = organization_factory()
        user = user_factory()
        membership = OrganizationMembership.objects.create(
            organization=org, user=user
        )
        assert membership.role == Role.MEMBER

    def test_invited_by_nullable(self, organization_factory, user_factory):
        org = organization_factory()
        user = user_factory()
        membership = OrganizationMembership.objects.create(
            organization=org, user=user
        )
        assert membership.invited_by is None

    def test_cascade_on_organization_delete(
        self, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        OrganizationMembership.objects.create(
            organization=org, user=user
        )
        org_id = org.id
        org.delete()
        assert not OrganizationMembership.objects.filter(
            organization_id=org_id
        ).exists()

    def test_str_representation(self, organization_factory, user_factory):
        org = organization_factory(name="Test Org")
        user = user_factory(email="member@example.com")
        membership = OrganizationMembership.objects.create(
            organization=org, user=user, role=Role.ADMIN
        )
        assert str(membership) == "member@example.com - Test Org (admin)"


@pytest.mark.django_db
class TestRoleEnum:
    def test_role_choices(self):
        choices = dict(Role.choices)
        assert choices["owner"] == "Owner"
        assert choices["admin"] == "Admin"
        assert choices["member"] == "Member"
