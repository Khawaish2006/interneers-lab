from django.urls import path
from . import views
from . import category_views

urlpatterns = [
    # ── Fixed URLs first ──────────────────────────────────
    path("", views.product_list),
    path("create/", views.product_create),
    path("bulk-create/", views.bulk_create),
    path("recently-updated/", views.recently_updated),

    # ── Category URLs (MUST be before <str:product_id>) ──
    path("categories/", category_views.category_list),
    path("categories/create/", category_views.category_create),
    path("categories/<str:category_id>/", category_views.category_get),
    path("categories/<str:category_id>/update/", category_views.category_update),
    path("categories/<str:category_id>/delete/", category_views.category_delete),

    # ── Variable URLs LAST ────────────────────────────────
    path("<str:product_id>/", views.product_get),
    path("<str:product_id>/update/", views.product_update),
    path("<str:product_id>/delete/", views.product_delete),
]