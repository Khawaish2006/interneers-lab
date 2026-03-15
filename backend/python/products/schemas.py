# products/schemas.py
# These are structured data classes for requests and responses
# Instead of passing raw dicts, we pass these clean objects

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

# ─── REQUEST MODELS (data coming IN) ──────────────────────

@dataclass
class CreateProductRequest:
    """Shape of data expected when creating a product"""
    name: str
    category: str
    price: Decimal
    brand: str
    description: str = ""
    quantity_in_warehouse: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        """Build a CreateProductRequest from raw dict"""
        return cls(
            name=data.get("name", ""),
            category=data.get("category", ""),
            price=data.get("price", 0),
            brand=data.get("brand", ""),
            description=data.get("description", ""),
            quantity_in_warehouse=int(data.get("quantity_in_warehouse", 0))
        )


@dataclass
class UpdateProductRequest:
    """Shape of data expected when updating a product (all fields optional)"""
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    quantity_in_warehouse: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name"),
            category=data.get("category"),
            price=data.get("price"),
            brand=data.get("brand"),
            description=data.get("description"),
            quantity_in_warehouse=data.get("quantity_in_warehouse")
        )

    def to_dict(self):
        """Return only the fields that were actually provided"""
        return {
            k: v for k, v in {
                "name": self.name,
                "category": self.category,
                "price": self.price,
                "brand": self.brand,
                "description": self.description,
                "quantity_in_warehouse": self.quantity_in_warehouse
            }.items() if v is not None
        }


# ─── RESPONSE MODELS (data going OUT) ─────────────────────

@dataclass
class ProductResponse:
    """Shape of data sent back in API responses"""
    id: str
    name: str
    category: str
    price: str
    brand: str
    description: str
    quantity_in_warehouse: int

    @classmethod
    def from_product(cls, product):
        """Build a ProductResponse from a MongoEngine Product object"""
        return cls(
            id=str(product.id),
            name=product.name,
            category=product.category,
            price=str(product.price),
            brand=product.brand,
            description=product.description,
            quantity_in_warehouse=product.quantity_in_warehouse
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "brand": self.brand,
            "description": self.description,
            "quantity_in_warehouse": self.quantity_in_warehouse
        }