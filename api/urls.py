from django.urls import include, path

urlpatterns = [
    path("api/v1/accounts/", include("api.v1.accounts.urls")),
]
