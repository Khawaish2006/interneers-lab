# products/services.py
# ONLY job: business logic and validation
# Calls repository for all DB operations

from decimal import Decimal, InvalidOperation
from .repository import ProductRepository
from .schemas import CreateProductRequest, UpdateProductRequest

class ProductService:

    @staticmethod
    def create_product(request: CreateProductRequest):
        """Validate and create a new product"""

        # Validate name
        if not request.name or not str(request.name).strip():
            raise ValueError("Name is required and cannot be empty")

        # Validate category
        if not request.category or not str(request.category).strip():
            raise ValueError("Category is required")

        # Validate brand
        if not request.brand or not str(request.brand).strip():
            raise ValueError("Brand is required")

        # Validate price
        try:
            price = Decimal(str(request.price))
            if price <= 0:
                raise ValueError("Price must be greater than zero")
        except InvalidOperation:
            raise ValueError("Price must be a valid number")

        # Validate quantity
        qty = request.quantity_in_warehouse
        if not isinstance(qty, int) or qty < 0:
            raise ValueError("Quantity must be a non-negative integer")

        # Build clean product data
        product_data = {
            "name": str(request.name).strip(),
            "description": str(request.description).strip(),
            "category": str(request.category).strip(),
            "price": price,
            "brand": str(request.brand).strip(),
            "quantity_in_warehouse": qty
        }

        return ProductRepository.create(product_data)

    @staticmethod
    def get_all_products():
        """Return all products"""
        return ProductRepository.get_all()

    @staticmethod
    def get_product_by_id(product_id: str):
        """Return one product or raise error"""
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product with id '{product_id}' not found")
        return product

    @staticmethod
    def update_product(product_id: str, request: UpdateProductRequest, partial: bool = False):
        """Update product — partial=True for PATCH, partial=False for PUT"""

        product = ProductService.get_product_by_id(product_id)
        fields = request.to_dict()

        # For PUT: all required fields must be present
        if not partial:
            required = ["name", "category", "price", "brand"]
            for field in required:
                if field not in fields:
                    raise ValueError(f"PUT requires all fields. Missing: {field}")

        # Validate price if provided
        if "price" in fields:
            try:
                price = Decimal(str(fields["price"]))
                if price <= 0:
                    raise ValueError("Price must be greater than zero")
                fields["price"] = price
            except InvalidOperation:
                raise ValueError("Price must be a valid number")

        # Validate quantity if provided
        if "quantity_in_warehouse" in fields:
            qty = fields["quantity_in_warehouse"]
            if int(qty) < 0:
                raise ValueError("Quantity cannot be negative")

        return ProductRepository.update(product, fields)

    @staticmethod
    def delete_product(product_id: str):
        """Delete a product"""
        product = ProductService.get_product_by_id(product_id)
        ProductRepository.delete(product)