from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)


class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "permissions"

    def __str__(self):
        return f"{self.name} ({self.codename})"


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    permissions = models.ManyToManyField(
        Permission, through="RoleHasPermission", related_name="permission"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


class RoleHasPermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role")
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="role_permission"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", self.get_or_create_superuser_role())
        return self.create_user(email, password, **extra_fields)

    def get_or_create_superuser_role(self):
        superuser_role, created = Role.objects.get_or_create(
            name="Superuser",
            defaults={"description": "Superuser role with all permissions"},
        )
        if created:
            permissions = Permission.objects.all()
            superuser_role.permissions.set(permissions)
            superuser_role.is_staff = True
        return superuser_role


class UserBase(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=False,
        null=False,
        max_length=254,
        db_index=True,
    )
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_role")
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["email"]

    def is_superuser(self):
        return self.role.name == "Superuser"

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True

        if self.role:
            action, model_name = perm.split("_", 1)
            return self.role.permissions.filter(name=perm).exists()

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        if self.role:

            return self.role.permissions.filter(
                codename__startswith=app_label.lower()
            ).exists()

        return False
