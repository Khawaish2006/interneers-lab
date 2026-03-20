# products/category_repository.py
from datetime import datetime, timezone
from .category_model import ProductCategory


def _now():
    return datetime.now(timezone.utc)


class CategoryRepository:

    @staticmethod
    def create(data: dict) -> ProductCategory:
        category = ProductCategory(
            title=data["title"],
            description=data.get("description", ""),
            created_at=_now(),
            updated_at=_now()
        )
        category.save()
        return category

    @staticmethod
    def get_all() -> list:
        return list(ProductCategory.objects.all())

    @staticmethod
    def get_by_id(category_id: str):
        try:
            return ProductCategory.objects.get(id=category_id)
        except Exception:
            return None

    @staticmethod
    def get_by_title(title: str):
        try:
            return ProductCategory.objects.get(title=title)
        except Exception:
            return None

    @staticmethod
    def update(category: ProductCategory, fields: dict) -> ProductCategory:
        for key, value in fields.items():
            setattr(category, key, value)
        category.updated_at = _now()
        category.save()
        return category

    @staticmethod
    def delete(category: ProductCategory) -> None:
        category.delete()