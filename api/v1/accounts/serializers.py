from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from api.v1.accounts.models import Permission, Role, UserBase


class PermissionSerializers(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "description"]


class RoleSerializers(serializers.ModelSerializer):
    permissions = PermissionSerializers(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Role
        fields = ["name", "description", "permissions", "permission_ids"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get("request")
        if request and request.method in ["PATCH", "PUT"]:
            representation.pop("permissions", None)
            representation["permission_ids"] = list(
                instance.permissions.values_list("id", flat=True)
            )

        return representation

    def create(self, validated_data):
        permission_ids = validated_data.pop("permission_ids", [])
        role = Role.objects.create(**validated_data)

        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop("permission_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)

        return instance


class RoleDisplaySerializers(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ["name"]


class UserSerializers(serializers.ModelSerializer):

    class Meta:
        model = UserBase
        fields = ["email", "password", "role", "phone_number"]


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ["email", "password", "phone_number"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])

        user_role, created = Role.objects.get_or_create(
            name="user", defaults={"description": "Default user role"}
        )
        validated_data["role"] = user_role

        return super().create(validated_data)


class UserDisplaySerializers(serializers.ModelSerializer):
    role = RoleDisplaySerializers(read_only=True)

    class Meta:
        model = UserBase
        fields = [
            "id",
            "email",
            "password",
            "role",
            "phone_number",
            "created_at",
            "updated_at",
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
