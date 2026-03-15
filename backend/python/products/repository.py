# products/repository.py
# ONLY job: read and write to MongoDB
# No validation, no business logic — just database operations

from .models import Product

class ProductRepository:

    @staticmethod
    def create(product_data: dict) -> Product:
        """Insert a new product document into MongoDB"""
        product = Product(**product_data)
        product.save()
        return product

    @staticmethod
    def get_all() -> list:
        """Fetch all product documents"""
        return list(Product.objects.all())

    @staticmethod
    def get_by_id(product_id: str):
        """Fetch one product by its MongoDB ID"""
        try:
            return Product.objects.get(id=product_id)
        except (Product.DoesNotExist, Exception):
            return None

    @staticmethod
    def update(product: Product, fields: dict) -> Product:
        """Update specific fields on a product"""
        for key, value in fields.items():
            setattr(product, key, value)
        product.save()
        return product

    @staticmethod
    def delete(product: Product) -> None:
        """Delete a product document"""
        product.delete()