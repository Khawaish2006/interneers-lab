from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"

    def ready(self):
        try:
            from .seed import seed_categories
            seed_categories()
        except Exception as e:
            print(f"Seeding failed: {e}")