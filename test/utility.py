from unittest.mock import MagicMock
from django.test import RequestFactory
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from pytest_factoryboy import register
from faker import Faker
import factory
from rest_framework.viewsets import ModelViewSet
from api.v1.accounts.models import UserBase, Role
from api.v1.accounts.permissions import UserPermission

fake = Faker()
User = get_user_model()


@pytest.fixture
def api_rf():
    """Provides a request factory for creating request objects."""
    return RequestFactory()


@pytest.fixture
def mock_user():
    """Creates a mock user with a role and permission structure."""
    user = MagicMock()
    user.is_authenticated = True
    user.id = 1
    role = MagicMock()
    role.permissions = MagicMock()
    user.role = role
    return user


@pytest.fixture
def permission_instance():
    """Provides an instance of the UserPermission class."""
    return UserPermission()


@pytest.fixture
def mock_view():
    """Creates a mock view with a queryset based on the UserBase model."""
    view = MagicMock()
    view.queryset = MagicMock()
    view.queryset.model = UserBase
    return view


@pytest.fixture
def authenticated_user_client():
    """Provides an authenticated API client for request tests."""
    client = APIClient()
    # Set up any necessary user authentication here if needed
    return client


@pytest.fixture
def api_client():
    """Provides a standard API client."""
    return APIClient()


# Define factory classes to generate instances of Role and User


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Iterator(["admin", "user", "friend"])


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    first_name = factory.LazyFunction(fake.first_name)
    last_name = factory.LazyFunction(fake.last_name)
    is_active = True
    role = factory.SubFactory(RoleFactory)


class AdminFactory(UserFactory):
    role = factory.SubFactory(RoleFactory, name="admin")
    is_staff = True
    is_superuser = False


class RegularUserFactory(UserFactory):
    role = factory.SubFactory(RoleFactory, name="user")


class FriendUserFactory(UserFactory):
    role = factory.SubFactory(RoleFactory, name="friend")


# Registering factories as fixtures


@pytest.fixture
def admin_user():
    """Creates and returns an instance of an admin user."""
    return AdminFactory()


@pytest.fixture
def regular_user():
    """Creates and returns an instance of a regular user."""
    return RegularUserFactory()


@pytest.fixture
def friend_user():
    """Creates and returns an instance of a user with the 'friend' role."""
    return FriendUserFactory()


@pytest.fixture
def role():
    """Provides a role instance for testing."""
    return RoleFactory()


# Create a dummy viewset for testing permissions


class DummyViewSet(ModelViewSet):
    """A dummy viewset for permission testing."""

    queryset = UserBase.objects.all()
    permission_classes = [UserPermission]


@pytest.fixture
def view_set():
    """Provides an instance of the DummyViewSet for testing."""
    return DummyViewSet()

