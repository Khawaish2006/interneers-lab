# products/category_service.py
from .category_repository import CategoryRepository


class CategoryService:

    @staticmethod
    def create_category(data: dict):
        # Validate title
        if not data.get("title") or not str(data["title"]).strip():
            raise ValueError("Category title is required")

        # Check for duplicates
        existing = CategoryRepository.get_by_title(data["title"].strip())
        if existing:
            raise ValueError(f"Category '{data['title']}' already exists")

        return CategoryRepository.create({
            "title": str(data["title"]).strip(),
            "description": str(data.get("description", "")).strip()
        })

    @staticmethod
    def get_all_categories():
        return CategoryRepository.get_all()

    @staticmethod
    def get_category(category_id: str):
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category with id '{category_id}' not found")
        return category

    @staticmethod
    def update_category(category_id: str, data: dict):
        category = CategoryService.get_category(category_id)
        fields = {k: v for k, v in data.items() if v is not None}
        return CategoryRepository.update(category, fields)

    @staticmethod
    def delete_category(category_id: str):
        category = CategoryService.get_category(category_id)
        CategoryRepository.delete(category)