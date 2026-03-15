# products/models.py
from mongoengine import (
    Document,
    StringField,
    DecimalField,
    IntField,
)

class Product(Document):
    """
    MongoDB Document for Product.
    Each instance = one document in the 'products' collection.
    """
    name = StringField(required=True, max_length=200)
    description = StringField(default="")
    category = StringField(required=True, max_length=100)
    price = DecimalField(required=True, precision=2, min_value=0.01)
    brand = StringField(required=True, max_length=100)
    quantity_in_warehouse = IntField(default=0, min_value=0)

    meta = {
        'collection': 'products'   # name of collection in MongoDB
    }

    def to_dict(self):
        """Convert to JSON-serializable dictionary"""
        return {
            "id": str(self.id),    # MongoDB _id converted to string
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "price": str(self.price),
            "brand": self.brand,
            "quantity_in_warehouse": self.quantity_in_warehouse
        }