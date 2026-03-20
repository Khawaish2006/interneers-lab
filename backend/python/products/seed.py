# products/seed.py
from .category_repository import CategoryRepository

DEFAULT_CATEGORIES = [
    {"title": "Electronics", "description": "Electronic devices and gadgets"},
    {"title": "Food", "description": "Food and beverages"},
    {"title": "Kitchen Essentials", "description": "Kitchen tools and appliances"},
    {"title": "Clothing", "description": "Apparel and accessories"},
    {"title": "Books", "description": "Books and educational materials"},
]

def seed_categories():
    print("Seeding categories...")
    for cat_data in DEFAULT_CATEGORIES:
        existing = CategoryRepository.get_by_title(cat_data["title"])
        if not existing:
            CategoryRepository.create(cat_data)
            print(f"  Created: {cat_data['title']}")
        else:
            print(f"  Already exists: {cat_data['title']}")
    print("Seeding complete.")