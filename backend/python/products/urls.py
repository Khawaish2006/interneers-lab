from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list),
    path("create/", views.product_create),
    path("<int:product_id>/", views.product_get),
    path("<int:product_id>/update/", views.product_update),
    path("<int:product_id>/delete/", views.product_delete),
]
