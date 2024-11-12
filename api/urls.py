from django.urls import include, path

urlpatterns = [
    path(
        "api/", 
        include(
            [
                path(
                    "v1/",
                    include(
                        [
                            path("accounts/", include("api.v1.accounts.urls")),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
