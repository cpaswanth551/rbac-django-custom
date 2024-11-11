from rest_framework.routers import DefaultRouter
from django.urls import include, path

from api.v1.accounts.views import PermissionViewSet, RoleViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"permission", PermissionViewSet, basename="permission")

urlpatterns = [path("", include(router.urls))]
