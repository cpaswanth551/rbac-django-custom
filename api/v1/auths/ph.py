from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):
    ACTION_PERMISSIONS = {
        "list": "list",
        "retrieve": "retrieve",
        "create": "create",
        "update": "update",
        "partial_update": "partial_update",
        "destroy": "destroy",
    }

    def has_permission(self, request, view):
        user = request.user
        action = self.ACTION_PERMISSIONS.get(view.action)

        if action:
            model_name = view.queryset.model.__name__.lower()
            permission_codename = f"{action}_{model_name}"
            return user.has_perm(permission_codename)
        return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        action = self.ACTION_PERMISSIONS.get(view.action)

        if action:
            model_name = obj.__class__.__name__.lower()
            permission_codename = f"{action}_{model_name}"
            return user.has_perm(permission_codename, obj)

        return user.is_authenticated
