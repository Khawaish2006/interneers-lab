"""
Product model used for schema and validation.
Storage is in-memory only (see products.views); this model is not persisted to the database.
"""
from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    """Product with basic info: name, description, category, price, brand, warehouse quantity."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    brand = models.CharField(max_length=100)
    quantity_in_warehouse = models.PositiveIntegerField(default=0)

    class Meta:
        managed = False  # Do not create DB table; we use in-memory storage only

    def to_dict(self):
        """Return product as a dictionary for JSON response."""
        return {
            "id": getattr(self, "_in_memory_id", None),
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "price": str(self.price),
            "brand": self.brand,
            "quantity_in_warehouse": self.quantity_in_warehouse,
        }
