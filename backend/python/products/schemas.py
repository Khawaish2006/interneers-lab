# products/schemas.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


# ── REQUEST MODELS ────────────────────────────────────────────

@dataclass
class CreateProductRequest:
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


# ── RESPONSE MODEL ────────────────────────────────────────────

@dataclass
class ProductResponse:
    id: str
    name: str
    category: dict        # ← changed from str to dict
    price: str
    brand: str
    description: str
    quantity_in_warehouse: int
    created_at: str = None
    updated_at: str = None

    @classmethod
    def from_product(cls, product):
        # safely convert category to dict
        category_data = None
        if product.category:
            try:
                # if category is a full object, call to_dict()
                category_data = product.category.to_dict()
            except Exception:
                # if category is just an ID reference, return minimal info
                category_data = {"id": str(product.category.id)}

        return cls(
            id=str(product.id),
            name=product.name,
            category=category_data,      # ← now a dict, not an object
            price=str(product.price),
            brand=product.brand,
            description=product.description,
            quantity_in_warehouse=product.quantity_in_warehouse,
            created_at=product.created_at.isoformat() if product.created_at else None,
            updated_at=product.updated_at.isoformat() if product.updated_at else None,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,   # ← already a dict, serializes fine
            "price": self.price,
            "brand": self.brand,
            "description": self.description,
            "quantity_in_warehouse": self.quantity_in_warehouse,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }