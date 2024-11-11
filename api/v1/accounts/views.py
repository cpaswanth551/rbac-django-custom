from rest_framework import viewsets, status
from rest_framework.response import Response

from rest_framework.decorators import action

from api.v1.accounts.models import Permission, Role, UserBase
from api.v1.accounts.serializers import (
    PermissionSerializers,
    RoleSerializers,
    UserDisplaySerializers,
    UserRegisterSerializer,
    UserSerializers,
)
from api.v1.auths.permissions import UserPermission


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserBase.objects.all()
    serializer_class = UserSerializers
    permission_classes = [UserPermission]

    def get_permissions(self):
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role.name in ["Superuser", "Admin"]:
            return UserBase.objects.all()
        return UserBase.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegisterSerializer
        if self.action in ["list", "retrieve"]:
            return UserDisplaySerializers
        return UserSerializers

    def create(self, request, *args, **kwargs):
        user_serializer = self.get_serializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        return Response(
            {
                "message": "User registered successfully",
                "user": {"id": user.id, "email": user.email, "role": user.role.name},
            },
            status=status.HTTP_201_CREATED,
        )


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [UserPermission]

    @action(detail=True, methods=["post"])
    def add_permissions(self, request, pk=None):
        role = self.get_object()
        permission_ids = request.data.get("permission_ids", [])

        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.add(*permissions)

        serializer = self.get_serializer(role)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def remove_permissions(self, request, pk=None):
        role = self.get_object()
        permission_ids = request.data.get("permission_ids", [])

        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.remove(*permissions)

        serializer = self.get_serializer(role)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def permissions(self, request, pk=None):
        role = self.get_object()
        permissions = role.permissions.all()
        serializer = PermissionSerializers(permissions, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializers
    permission_classes = [UserPermission]
