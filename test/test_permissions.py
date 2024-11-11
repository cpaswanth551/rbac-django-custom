from api.v1.accounts.models import Permission
from test.utility import *


class TestUserPermission:

    def test_unauthenticated_user(self, api_rf, mock_view, permission_instance):
        request = api_rf.get("/")
        request.user = MagicMock(is_authenticated=False)

        assert permission_instance.has_permission(request, mock_view) is False

    def test_superuser_has_permission(
        self, api_rf, mock_user, mock_view, permission_instance
    ):
        request = api_rf.get("/")
        mock_user.role.name = "Superuser"
        request.user = mock_user
        mock_view.action = "list"

        assert permission_instance.has_permission(request, mock_view) is True

    def test_create_userbase_without_auth(self, api_rf, mock_view, permission_instance):
        request = api_rf.post("/")
        request.user = MagicMock(is_authenticated=False)
        mock_view.action = "create"

        assert permission_instance.has_permission(request, mock_view) is True

    def test_user_with_permission(
        self, api_rf, mock_user, mock_view, permission_instance
    ):
        request = api_rf.get("/")
        request.user = mock_user
        mock_view.action = "list"
        mock_user.role.name = "Regular"
        mock_user.role.permissions.filter.return_value.exists.return_value = True

        assert permission_instance.has_permission(request, mock_view) is True

    def test_user_without_permission(
        self, api_rf, mock_user, mock_view, permission_instance
    ):
        request = api_rf.get("/")
        request.user = mock_user
        mock_view.action = "list"
        mock_user.role.name = "Regular"
        mock_user.role.permissions.filter.return_value.exists.return_value = False

    def test_invalid_action(self, api_rf, mock_user, mock_view, permission_instance):
        request = api_rf.get("/")
        request.user = mock_user
        mock_view.action = "invalid_action"

        assert permission_instance.has_permission(request, mock_view) is False

    def test_object_permission_superuser(
        self, api_rf, mock_user, mock_view, permission_instance
    ):
        request = api_rf.get("/")
        mock_user.role.name = "Superuser"
        request.user = mock_user
        obj = MagicMock()

        assert (
            permission_instance.has_object_permission(request, mock_view, obj) is True
        )

    def test_object_permission_own_user(
        self, api_rf, mock_user, mock_view, permission_instance
    ):
        request = api_rf.get("/")
        request.user = mock_user
        obj = MagicMock(spec=UserBase)
        obj.id = mock_user.id

        assert (
            permission_instance.has_object_permission(request, mock_view, obj) is True
        )

    def test_object_permission_other_user(
        self, api_rf, mock_user, mock_view, permission_instance
    ):
        request = api_rf.get("/")
        request.user = mock_user
        mock_user.role.name = "Regular"
        obj = MagicMock(spec=UserBase)
        obj.id = mock_user.id + 1
        mock_view.action = "retrieve"
        mock_user.role.permissions.filter.return_value.exists.return_value = False

        assert (
            permission_instance.has_object_permission(request, mock_view, obj) is False
        )

    def test_object_permission_with_permission(
        self, api_rf, mock_user, mock_view, permission_instance
    ):
        request = api_rf.get("/")
        request.user = mock_user
        mock_user.role.name = "Regular"
        obj = MagicMock()
        obj.__class__.__name__ = "UserBase"
        mock_view.action = "retrieve"
        mock_user.role.permissions.filter.return_value.exists.return_value = True

        assert (
            permission_instance.has_object_permission(request, mock_view, obj) is True
        )

    @pytest.mark.parametrize(
        "action, expected_permission",
        [
            ("list", "list_userbase"),
            ("retrieve", "view_userbase"),
            ("create", "add_userbase"),
            ("update", "change_userbase"),
            ("partial_update", "change_userbase"),
            ("destroy", "delete_userbase"),
        ],
    )
    def test_permission_codename_mapping(
        self, api_rf, mock_user, view_set, action, expected_permission
    ):
        request = api_rf.get("/")
        request.user = mock_user
        mock_user.is_authenticated = True
        mock_user.role.name = "Regular"
        view_set.action = action

        mock_permissions = MagicMock()
        mock_user.role.permissions = mock_permissions

        permission_instance = UserPermission()
        result = permission_instance.has_permission(request, view_set)

        assert result is True
