# products/category_model.py
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone

class ProductCategory(Document):
    title = StringField(required=True, max_length=100, unique=True)
    description = StringField(default="")
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        'collection': 'product_categories'
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }