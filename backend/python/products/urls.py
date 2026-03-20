from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list),
    path("create/", views.product_create),
    path("recently-updated/", views.recently_updated),    # ← NEW
    path("<str:product_id>/", views.product_get),
    path("<str:product_id>/update/", views.product_update),
    path("<str:product_id>/delete/", views.product_delete),
]