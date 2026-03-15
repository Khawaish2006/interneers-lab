from django.urls import path, include

urlpatterns = [
    # admin/ removed because django.contrib.admin is not in INSTALLED_APPS
    path("api/products/", include("products.urls")),
]


