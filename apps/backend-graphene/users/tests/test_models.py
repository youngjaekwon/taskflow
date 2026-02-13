import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCustomUser:
    def test_create_user_with_email(self, user_factory):
        user = user_factory(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.check_password("testpass123!")
        assert not user.is_superuser
        assert not user.email_verified

    def test_username_auto_generated_when_blank(self):
        user = User.objects.create_user(
            email="auto@example.com",
            password="testpass123!",
        )
        assert user.username.startswith("user_")
        assert len(user.username) == 13  # "user_" + 8 hex chars

    def test_username_preserved_when_provided(self):
        user = User.objects.create_user(
            email="manual@example.com",
            password="testpass123!",
            username="custom_name",
        )
        assert user.username == "custom_name"

    def test_email_is_unique(self, user_factory):
        user_factory(email="dup@example.com")
        with pytest.raises(Exception):
            user_factory(email="dup@example.com")

    def test_str_returns_email(self, user_factory):
        user = user_factory(email="str@example.com")
        assert str(user) == "str@example.com"

    def test_email_is_username_field(self):
        assert User.USERNAME_FIELD == "email"

    def test_profile_image_defaults_to_none(self, user_factory):
        user = user_factory()
        assert not user.profile_image

    def test_email_verified_defaults_to_false(self, user_factory):
        user = user_factory()
        assert user.email_verified is False
