from django.urls import reverse
import pytest
from rest_framework import status
from unittest.mock import patch

from api.v1.accounts.models import UserBase
from test.utility import *


@pytest.fixture
def user_role():
    return Role.objects.create(name="User")


@pytest.fixture
def admin_role():
    return Role.objects.create(name="Admin")


@pytest.fixture
def superuser_role():
    return Role.objects.create(name="Superuser")


@pytest.fixture
def regular_user(user_role):
    user = UserBase.objects.create(
        email="user@example.com",
        password="securepass123",
        role=user_role,
        is_active=True,
    )
    user.set_password("securepass123")
    user.save()
    return user


@pytest.fixture
def admin_user(admin_role):
    user = UserBase.objects.create(
        email="admin@example.com",
        password="adminpass123",
        role=admin_role,
        is_active=True,
        is_staff=True,
    )
    user.set_password("adminpass123")
    user.save()
    return user


@pytest.fixture
def superuser(superuser_role):
    user = UserBase.objects.create(
        email="superuser@example.com",
        password="superpass123",
        role=superuser_role,
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    user.set_password("superpass123")
    user.save()
    return user


class MockUserPermission:
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role.name in ["Superuser", "Admin"]:
            return True
        if view.action in ["create"]:
            return True
        if view.action in ["retrieve", "update", "partial_update", "destroy"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role.name in ["Superuser", "Admin"]:
            return True
        return obj.id == user.id


@pytest.mark.django_db
class TestUserViewSet:

    def setup_method(self):
        self.list_url = reverse("user-list")

        patcher = patch("api.v1.accounts.permissions", MockUserPermission)
        self.mock_permission = patcher.start()

    def get_detail_url(self, user_id):
        return reverse("user-detail", kwargs={"pk": user_id})

    def test_list_users_as_superuser(self, api_client, superuser, regular_user):
        api_client.force_authenticate(user=superuser)
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_list_users_as_admin(self, api_client, admin_user_, regular_user_):
        api_client.force_authenticate(user=admin_user_)
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
