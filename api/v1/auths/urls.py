from rest_framework.routers import DefaultRouter
from django.urls import include, path

from api.v1.auths.views import *

router = DefaultRouter()
router.register(r"", AuthViewSet, basename="auth")

urlpatterns = [path("", include(router.urls))]
