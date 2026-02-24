import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from labels.models import Label


@pytest.mark.django_db
class TestLabelModel:
    def test_default_color(self, organization_factory):
        org = organization_factory()
        label = Label.objects.create(organization=org, name="Test")
        assert label.color == "#808080"

    def test_custom_color(self, label_factory, organization_factory):
        org = organization_factory()
        label = label_factory(organization=org, color="#FF5733")
        assert label.color == "#FF5733"

    def test_unique_together_organization_name(
        self, label_factory, organization_factory
    ):
        org = organization_factory()
        label_factory(organization=org, name="Bug")
        with pytest.raises(IntegrityError):
            label_factory(organization=org, name="Bug")

    def test_same_name_different_org(self, label_factory, organization_factory):
        org1 = organization_factory()
        org2 = organization_factory()
        label_factory(organization=org1, name="Bug")
        label2 = label_factory(organization=org2, name="Bug")
        assert label2.name == "Bug"

    def test_color_regex_validation_valid(self, label_factory, organization_factory):
        org = organization_factory()
        label = label_factory(organization=org, color="#AABBCC")
        label.full_clean()  # should not raise

    def test_color_regex_validation_invalid(self, label_factory, organization_factory):
        org = organization_factory()
        label = label_factory(organization=org, color="red")
        with pytest.raises(ValidationError):
            label.full_clean()

    def test_color_regex_validation_short(self, label_factory, organization_factory):
        org = organization_factory()
        label = label_factory(organization=org, color="#FFF")
        with pytest.raises(ValidationError):
            label.full_clean()

    def test_created_by_set_null_on_delete(
        self, label_factory, organization_factory, user_factory
    ):
        org = organization_factory()
        creator = user_factory(email_verified=True)
        label = label_factory(organization=org, created_by=creator)
        creator.delete()
        label.refresh_from_db()
        assert label.created_by is None

    def test_cascade_delete_with_organization(
        self, label_factory, organization_factory
    ):
        org = organization_factory()
        org_id = org.pk
        label_factory(organization=org)
        label_factory(organization=org)
        assert Label.objects.filter(organization_id=org_id).count() == 2
        org.delete()
        assert Label.objects.filter(organization_id=org_id).count() == 0

    def test_str(self, label_factory, organization_factory):
        org = organization_factory()
        label = label_factory(organization=org, name="Feature")
        assert str(label) == "Feature"
