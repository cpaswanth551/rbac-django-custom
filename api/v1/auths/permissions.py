from rest_framework.permissions import BasePermission

from api.v1.accounts.models import RoleHasPermission, UserBase


class UserPermission(BasePermission):
    ACTION_PERMISSIONS = {
        "list": "list",
        "retrieve": "view",
        "create": "add",
        "update": "change",
        "partial_update": "change",
        "destroy": "delete",
    }

    def has_permission(self, request, view):
        print("permission is called")
        user = request.user
        if (
            view.action == "create"
            and hasattr(view, "queryset")
            and view.queryset.model.__name__.lower() == "userbase"
        ):
            return True

        if not user.is_authenticated:
            return False

        if user.role.name == "Superuser":
            return True

        action = self.ACTION_PERMISSIONS.get(view.action)
        if not action:
            return False

        model_name = view.queryset.model.__name__.lower()
        permission_codename = f"{action}_{model_name}"

        if user.role.permissions.filter(codename=permission_codename).exists():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role.name == "Superuser":
            return True

        if isinstance(obj, UserBase) and obj.id == user.id:
            return True

        action = self.ACTION_PERMISSIONS.get(view.action)
        if not action:
            return False

        model_name = obj.__class__.__name__.lower()
        permission_codename = f"{action}_{model_name}"

        if user.role.permissions.filter(codename=permission_codename).exists():
            return True
        return False
