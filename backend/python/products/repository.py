# products/repository.py
from datetime import datetime, timezone
from .models import Product
from .category_model import ProductCategory


def _now():
    return datetime.now(timezone.utc)


class ProductRepository:

    @staticmethod
    def create(product_data: dict) -> Product:
        product_data["created_at"] = _now()
        product_data["updated_at"] = _now()
        product = Product(**product_data)
        product.save()
        return product

    @staticmethod
    def bulk_create(products_data: list) -> list:
        """Create multiple products at once"""
        created = []
        for data in products_data:
            data["created_at"] = _now()
            data["updated_at"] = _now()
            product = Product(**data)
            product.save()
            created.append(product)
        return created

    @staticmethod
    def get_all(filters: dict = None) -> list:
        """Get all products with optional filters"""
        queryset = Product.objects

        if filters:
            # filter by category id
            if "category" in filters:
                queryset = queryset.filter(category=filters["category"])
            # filter by brand
            if "brand" in filters:
                queryset = queryset.filter(brand__icontains=filters["brand"])
            # filter by min price
            if "min_price" in filters:
                queryset = queryset.filter(price__gte=filters["min_price"])
            # filter by max price
            if "max_price" in filters:
                queryset = queryset.filter(price__lte=filters["max_price"])

        return list(queryset.all())

    @staticmethod
    def get_all_sorted(sort: str, filters: dict = None) -> list:
        queryset = Product.objects
        if filters:
            if "category" in filters:
                queryset = queryset.filter(category=filters["category"])
            if "brand" in filters:
                queryset = queryset.filter(brand__icontains=filters["brand"])
        if sort == "newest":
            return list(queryset.order_by("-created_at"))
        elif sort == "oldest":
            return list(queryset.order_by("created_at"))
        return list(queryset.all())

    @staticmethod
    def get_by_id(product_id: str):
        try:
            return Product.objects.get(id=product_id)
        except Exception:
            return None

    @staticmethod
    def get_by_category(category) -> list:
        return list(Product.objects.filter(category=category))

    @staticmethod
    def update(product: Product, fields: dict) -> Product:
        for key, value in fields.items():
            setattr(product, key, value)
        product.updated_at = _now()
        product.save()
        return product

    @staticmethod
    def delete(product: Product) -> None:
        product.delete()

    @staticmethod
    def get_recently_updated(days: int = 7) -> list:
        from datetime import timedelta
        cutoff = _now() - timedelta(days=days)
        return list(Product.objects.filter(updated_at__gte=cutoff))