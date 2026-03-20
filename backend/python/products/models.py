# products/models.py
from mongoengine import (
    Document,
    StringField,
    DecimalField,
    IntField,
    DateTimeField,
    ReferenceField,    # ← NEW — links to another document
    CASCADE            # ← NEW — what happens when category is deleted
)
from datetime import datetime, timezone
from .category_model import ProductCategory


class Product(Document):
    name = StringField(required=True, max_length=200)
    description = StringField(default="")

    # ReferenceField links Product to ProductCategory
    # instead of storing "Electronics" (string),
    # it stores the ID of the Electronics category document
    category = ReferenceField(ProductCategory, required=True)

    price = DecimalField(required=True, precision=2, min_value=0.01)
    brand = StringField(required=True, max_length=100)
    quantity_in_warehouse = IntField(default=0, min_value=0)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        'collection': 'products'
    }

    def to_dict(self):
        # category is now a full object, not just a string
        category_data = None
        if self.category:
            try:
                category_data = self.category.to_dict()
            except Exception:
                category_data = {"id": str(self.category.id)}

        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": category_data,
            "price": str(self.price),
            "brand": self.brand,
            "quantity_in_warehouse": self.quantity_in_warehouse,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }