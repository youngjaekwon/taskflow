import pytest

from projects.models import Project, ProjectMembership


@pytest.mark.django_db
class TestProjectModel:
    def test_create_project(self, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(name="Test Project", organization=org)
        assert project.name == "Test Project"
        assert project.slug == "test-project"
        assert project.organization == org

    def test_slug_auto_generated_from_name(self, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(name="My Cool Project", organization=org)
        assert project.slug == "my-cool-project"

    def test_slug_unique_within_organization(
        self, project_factory, organization_factory
    ):
        org = organization_factory()
        p1 = project_factory(name="Duplicate", organization=org)
        p2 = project_factory(name="Duplicate", organization=org)
        assert p1.slug == "duplicate"
        assert p2.slug == "duplicate-2"

    def test_slug_unique_with_multiple_duplicates(
        self, project_factory, organization_factory
    ):
        org = organization_factory()
        p1 = project_factory(name="Same", organization=org)
        p2 = project_factory(name="Same", organization=org)
        p3 = project_factory(name="Same", organization=org)
        assert p1.slug == "same"
        assert p2.slug == "same-2"
        assert p3.slug == "same-3"

    def test_same_slug_allowed_in_different_organizations(
        self, project_factory, organization_factory
    ):
        org1 = organization_factory()
        org2 = organization_factory()
        p1 = project_factory(name="Same Name", organization=org1)
        p2 = project_factory(name="Same Name", organization=org2)
        assert p1.slug == "same-name"
        assert p2.slug == "same-name"

    def test_description_defaults_to_blank(self, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(organization=org)
        assert project.description == ""

    def test_str_returns_name(self, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(name="Str Test", organization=org)
        assert str(project) == "Str Test"

    def test_created_by_set_null_on_user_delete(
        self, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        user = user_factory()
        project = project_factory(organization=org, created_by=user)
        user.delete()
        project.refresh_from_db()
        assert project.created_by is None

    def test_cascade_on_organization_delete(
        self, project_factory, organization_factory
    ):
        org = organization_factory()
        project_factory(organization=org)
        project_factory(organization=org)
        org_id = org.id
        org.delete()
        assert not Project.objects.filter(organization_id=org_id).exists()

    def test_slug_fallback_for_empty_name(self, project_factory, organization_factory):
        org = organization_factory()
        project = project_factory(name="", organization=org)
        assert project.slug == "project"


@pytest.mark.django_db
class TestProjectMembershipModel:
    def test_create_membership(
        self, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        project = project_factory(organization=org)
        user = user_factory()
        membership = ProjectMembership.objects.create(project=project, user=user)
        assert membership.project == project
        assert membership.user == user

    def test_unique_together_constraint(
        self, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        project = project_factory(organization=org)
        user = user_factory()
        ProjectMembership.objects.create(project=project, user=user)
        with pytest.raises(Exception):
            ProjectMembership.objects.create(project=project, user=user)

    def test_added_by_nullable(
        self, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        project = project_factory(organization=org)
        user = user_factory()
        membership = ProjectMembership.objects.create(project=project, user=user)
        assert membership.added_by is None

    def test_cascade_on_project_delete(
        self, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        project = project_factory(organization=org)
        user = user_factory()
        ProjectMembership.objects.create(project=project, user=user)
        project_id = project.id
        project.delete()
        assert not ProjectMembership.objects.filter(project_id=project_id).exists()

    def test_str_representation(
        self, project_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        project = project_factory(name="Test Proj", organization=org)
        user = user_factory(email="member@example.com")
        membership = ProjectMembership.objects.create(project=project, user=user)
        assert str(membership) == "member@example.com - Test Proj"
