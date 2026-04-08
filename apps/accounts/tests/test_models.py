import pytest

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234")
        assert user.email == "user@example.com"
        assert user.check_password("pass1234")
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_create_user_without_email_raises(self):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="pass1234")

    def test_create_superuser(self):
        user = User.objects.create_superuser(email="admin@example.com", password="admin1234")
        assert user.is_staff
        assert user.is_superuser
        assert user.is_active

    def test_create_superuser_not_staff_raises(self):
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(email="a@b.com", password="x", is_staff=False)

    def test_create_superuser_not_superuser_raises(self):
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(email="a@b.com", password="x", is_superuser=False)

    def test_email_is_normalized(self):
        user = User.objects.create_user(email="User@EXAMPLE.COM", password="pass1234")
        assert user.email == "User@example.com"

    def test_str_returns_email(self):
        user = User.objects.create_user(email="user@test.com", password="pass1234")
        assert str(user) == "user@test.com"

    def test_username_field_is_email(self):
        assert User.USERNAME_FIELD == "email"

    def test_is_owner_property(self):
        user = User.objects.create_user(email="owner@test.com", password="pass1234", role="owner")
        assert user.is_owner
        regular = User.objects.create_user(email="regular@test.com", password="pass1234")
        assert not regular.is_owner
