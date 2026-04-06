import os
import sys

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"

    def ready(self):
        # Avoid running seed twice on `runserver` (parent + autoreload child).
        if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
            return
        # Ping first so we never print "Seeding categories..." when Mongo is down.
        try:
            from mongoengine.connection import get_connection

            get_connection().admin.command("ping")
        except Exception:
            print(
                "[products] MongoDB not running (localhost:27019). "
                "Category seed skipped — start with: docker compose up -d"
            )
            return
        try:
            from .seed import seed_categories

            seed_categories()
        except Exception as e:
            print(f"[products] Category seeding failed: {e}")