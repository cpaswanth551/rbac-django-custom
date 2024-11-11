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
