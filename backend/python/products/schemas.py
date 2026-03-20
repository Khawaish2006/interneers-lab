# products/schemas.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


# ─── REQUEST MODELS (data coming IN) ──────────────────────────

@dataclass
class CreateProductRequest:
    """
    Shape of data expected when creating a product.
    NO timestamps here — user should never send these.
    Timestamps are set automatically in the repository.
    """
    name: str
    category: str
    price: Decimal
    brand: str
    description: str = ""
    quantity_in_warehouse: int = 0

    @classmethod
    def from_dict(cls, data: dict):
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
    """
    Shape of data expected when updating a product.
    All fields optional — user only sends what they want to change.
    NO timestamps here — updated_at is set automatically in repository.
    """
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
        """Return only fields that were actually provided (not None)"""
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


# ─── RESPONSE MODELS (data going OUT) ─────────────────────────

@dataclass
class ProductResponse:
    """
    Shape of data sent back in every API response.
    Timestamps are included here because we SHOW them to the user.
    """
    id: str
    name: str
    category: str
    price: str
    brand: str
    description: str
    quantity_in_warehouse: int
    created_at: str = None    # shown in response, set by system
    updated_at: str = None    # shown in response, set by system

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
            quantity_in_warehouse=product.quantity_in_warehouse,
            # convert datetime to readable string, handle if None
            created_at=product.created_at.isoformat() if product.created_at else None,
            updated_at=product.updated_at.isoformat() if product.updated_at else None,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "brand": self.brand,
            "description": self.description,
            "quantity_in_warehouse": self.quantity_in_warehouse,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }