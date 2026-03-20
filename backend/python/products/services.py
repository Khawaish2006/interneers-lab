# products/services.py
import csv
import io
from decimal import Decimal, InvalidOperation
from .repository import ProductRepository
from .category_repository import CategoryRepository
from .schemas import CreateProductRequest, UpdateProductRequest


class ProductService:

    @staticmethod
    def create_product(request: CreateProductRequest):
        # Validate name
        if not request.name or not str(request.name).strip():
            raise ValueError("Name is required")

        # Validate category — must be a valid category ID now
        category = CategoryRepository.get_by_id(request.category)
        if not category:
            raise ValueError(f"Category with id '{request.category}' not found")

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

        product_data = {
            "name": str(request.name).strip(),
            "description": str(request.description).strip(),
            "category": category,    # pass the actual category object
            "price": price,
            "brand": str(request.brand).strip(),
            "quantity_in_warehouse": qty
        }

        return ProductRepository.create(product_data)

    @staticmethod
    def get_all_products(sort: str = None, filters: dict = None):
        if sort:
            return ProductRepository.get_all_sorted(sort, filters)
        return ProductRepository.get_all(filters)

    @staticmethod
    def get_product_by_id(product_id: str):
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product with id '{product_id}' not found")
        return product

    @staticmethod
    def get_products_by_category(category_id: str):
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category not found")
        return ProductRepository.get_by_category(category)

    @staticmethod
    def update_product(product_id: str, request: UpdateProductRequest, partial: bool = False):
        product = ProductService.get_product_by_id(product_id)
        fields = request.to_dict()

        if not partial:
            required = ["name", "category", "price", "brand"]
            for field in required:
                if field not in fields:
                    raise ValueError(f"PUT requires all fields. Missing: {field}")

        # If category is being updated, validate it
        if "category" in fields:
            category = CategoryRepository.get_by_id(fields["category"])
            if not category:
                raise ValueError(f"Category not found")
            fields["category"] = category

        if "price" in fields:
            try:
                price = Decimal(str(fields["price"]))
                if price <= 0:
                    raise ValueError("Price must be greater than zero")
                fields["price"] = price
            except InvalidOperation:
                raise ValueError("Price must be a valid number")

        return ProductRepository.update(product, fields)

    @staticmethod
    def delete_product(product_id: str):
        product = ProductService.get_product_by_id(product_id)
        ProductRepository.delete(product)

    @staticmethod
    def bulk_create_from_csv(csv_content: str):
        """Parse CSV and create multiple products"""
        reader = csv.DictReader(io.StringIO(csv_content))
        results = {"created": [], "errors": []}

        for i, row in enumerate(reader):
            try:
                # find category by title from CSV
                category = CategoryRepository.get_by_title(row.get("category", ""))
                if not category:
                    raise ValueError(f"Category '{row.get('category')}' not found")

                product_data = {
                    "name": row["name"].strip(),
                    "description": row.get("description", "").strip(),
                    "category": category,
                    "price": Decimal(str(row["price"]).strip()),
                    "brand": row["brand"].strip(),
                    "quantity_in_warehouse": int(row.get("quantity_in_warehouse", 0))
                }
                product = ProductRepository.create(product_data)
                results["created"].append(product.to_dict())
            except Exception as e:
                results["errors"].append({"row": i + 1, "error": str(e)})

        return results

    @staticmethod
    def get_recently_updated(days: int = 7):
        return ProductRepository.get_recently_updated(days)