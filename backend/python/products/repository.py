from datetime import datetime, timezone
from .models import Product

def _now():
    """Returns current UTC time"""
    return datetime.now(timezone.utc)

class ProductRepository:

    @staticmethod
    def create(product_data: dict) -> Product:
        now = _now()
        product_data["created_at"] = now   # set once
        product_data["updated_at"] = now   # same as created_at initially
        product = Product(**product_data)
        product.save()
        return product

    @staticmethod
    def get_all() -> list:
        return list(Product.objects.all())

    @staticmethod
    def get_by_id(product_id: str):
        try:
            return Product.objects.get(id=product_id)
        except Exception:
            return None

    @staticmethod
    def update(product: Product, fields: dict) -> Product:
        for key, value in fields.items():
            setattr(product, key, value)
        product.updated_at = _now()    # always update this on every change
        product.save()
        return product

    @staticmethod
    def delete(product: Product) -> None:
        product.delete()

    # ── NEW METHODS using audit columns ──────────────────────

    @staticmethod
    def get_all_sorted(sort: str) -> list:
        """Sort products by created_at"""
        if sort == "newest":
            return list(Product.objects.order_by("-created_at"))  # - means descending
        elif sort == "oldest":
            return list(Product.objects.order_by("created_at"))   # ascending
        return list(Product.objects.all())

    @staticmethod
    def get_recently_updated(days: int = 7) -> list:
        """Get products updated in the last N days"""
        from datetime import timedelta
        cutoff = _now() - timedelta(days=days)
        return list(Product.objects.filter(updated_at__gte=cutoff))