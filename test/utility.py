from unittest.mock import MagicMock
from django.test import RequestFactory
import pytest

from api.v1.accounts.models import UserBase
from api.v1.accounts.permissions import UserPermission


@pytest.fixture
def api_rf():
    return RequestFactory()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.is_authenticated = True
    user.id = 1
    role = MagicMock()
    role.permissions = MagicMock()
    user.role = role
    return user


@pytest.fixture
def permission_instance():
    return UserPermission()


@pytest.fixture
def mock_view():
    view = MagicMock()
    view.queryset = MagicMock()
    view.queryset.model = UserBase
    return view
