"""
Product APIs: in-memory CRUD with validation.
All operations use a global in-memory store; no database persistence.
"""
import json
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Product

# In-memory store: id -> product dict (all APIs operate on this only)
_product_store = {}
_next_id = 1


def _get_request_data(request):
    """
    Parse request body as JSON, or fall back to request.POST for form data.
    Return (data_dict, error_response). If error, error_response is a JsonResponse.
    """
    raw = getattr(request, "body", None) or b""
    data = {}
    if raw:
        ct = (request.content_type or "").lower()
        if "application/json" in ct or not ct:
            try:
                data = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                return None, JsonResponse(
                    {"error": "Invalid JSON", "detail": str(e)},
                    status=400,
                )
    if not data and request.method == "POST" and request.POST:
        # Fallback: form-encoded body (e.g. from browser form or some clients)
        data = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description") or "",
            "category": request.POST.get("category"),
            "price": request.POST.get("price"),
            "brand": request.POST.get("brand"),
            "quantity_in_warehouse": request.POST.get("quantity_in_warehouse") or "0",
        }
    return data, None


def _validate_and_build_product(data, instance=None):
    """
    Validate data and return (product_dict, error_response).
    If instance is given, it's used for partial update (only provided fields updated).
    """
    # Allowed fields and their types for validation
    field_names = ["name", "description", "category", "price", "brand", "quantity_in_warehouse"]

    for key in data:
        if key not in field_names:
            return None, JsonResponse(
                {"error": f"Unknown field: {key}. Allowed: {field_names}"},
                status=400,
            )

    # Build a full dict for validation (merge with existing for PATCH)
    if instance:
        base = dict(instance)
        base.update(data)
        data = base

    # Required fields for create
    required = ["name", "category", "price", "brand"]
    for field in required:
        if field not in data or data[field] is None:
            return None, JsonResponse(
                {"error": f"Missing required field: {field}"},
                status=400,
            )

    # Optional with defaults
    if "description" not in data:
        data["description"] = ""
    if "quantity_in_warehouse" not in data:
        data["quantity_in_warehouse"] = 0

    # Coerce types (form data or JSON may send strings)
    try:
        price_val = data["price"]
        if not isinstance(price_val, (int, float, Decimal)):
            price_val = Decimal(str(price_val).strip())
        else:
            price_val = Decimal(str(price_val))
        qty = data["quantity_in_warehouse"]
        if not isinstance(qty, int):
            qty = int(float(qty)) if qty not in (None, "") else 0
        data["price"] = price_val
        data["quantity_in_warehouse"] = qty
    except (ValueError, InvalidOperation, TypeError) as e:
        return None, JsonResponse(
            {"error": "Invalid number for price or quantity_in_warehouse", "detail": str(e)},
            status=400,
        )

    # Use Django Model for validation
    try:
        p = Product(
            name=str(data["name"]).strip() if data["name"] is not None else "",
            description=str(data["description"]).strip() if data["description"] is not None else "",
            category=str(data["category"]).strip() if data["category"] is not None else "",
            price=data["price"],
            brand=str(data["brand"]).strip() if data["brand"] is not None else "",
            quantity_in_warehouse=data["quantity_in_warehouse"],
        )
        p.full_clean()
    except Exception as e:
        err_details = getattr(e, "message_dict", None) or getattr(e, "error_dict", None)
        if err_details is not None:
            # Make JSON-serializable (Django may use lazy translation objects)
            details = {k: [str(m) for m in (v if isinstance(v, (list, tuple)) else [v])] for k, v in err_details.items()}
            return None, JsonResponse(
                {"error": "Validation failed", "details": details},
                status=400,
            )
        return None, JsonResponse(
            {"error": "Validation failed", "detail": str(e)},
            status=400,
        )

    return {
        "name": p.name,
        "description": p.description,
        "category": p.category,
        "price": str(p.price),
        "brand": p.brand,
        "quantity_in_warehouse": p.quantity_in_warehouse,
    }, None


@csrf_exempt
@require_http_methods(["POST"])
def product_create(request):
    """Create a new product. Body: JSON with name, description?, category, price, brand, quantity_in_warehouse?."""
    data, err = _get_request_data(request)
    if err:
        return err
    if not data:
        return JsonResponse({
            "error": "Request body is required",
            "hint": "Send JSON with at least: name, category, price, brand. Use Content-Type: application/json",
        }, status=400)

    product_dict, err = _validate_and_build_product(data)
    if err:
        return err

    global _product_store, _next_id
    product_id = _next_id
    _next_id += 1
    product_dict["id"] = product_id
    _product_store[product_id] = product_dict

    return JsonResponse(product_dict, status=201)


@require_http_methods(["GET"])
def product_list(request):
    """Return all products (in-memory list)."""
    return JsonResponse({"products": list(_product_store.values()), "count": len(_product_store)})


@require_http_methods(["GET"])
def product_get(request, product_id):
    """Return a single product by id."""
    try:
        pid = int(product_id)
    except ValueError:
        return JsonResponse({"error": "Invalid product id"}, status=400)

    if pid not in _product_store:
        return JsonResponse({"error": "Product not found"}, status=404)

    return JsonResponse(_product_store[pid])


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def product_update(request, product_id):
    """Update a product. PUT = full replace, PATCH = partial update."""
    try:
        pid = int(product_id)
    except ValueError:
        return JsonResponse({"error": "Invalid product id"}, status=400)

    if pid not in _product_store:
        return JsonResponse({"error": "Product not found"}, status=404)

    data, err = _get_request_data(request)
    if err:
        return err
    if not data:
        return JsonResponse({"error": "Request body is required"}, status=400)

    existing = _product_store[pid]
    if request.method == "PUT":
        # Full replace: require all required fields
        product_dict, err = _validate_and_build_product(data)
    else:
        # PATCH: only validate provided fields, merge with existing
        product_dict, err = _validate_and_build_product(data, instance=existing)

    if err:
        return err

    product_dict["id"] = pid
    _product_store[pid] = product_dict
    return JsonResponse(product_dict)


@csrf_exempt
@require_http_methods(["DELETE"])
def product_delete(request, product_id):
    """Delete a product (in-memory only)."""
    try:
        pid = int(product_id)
    except ValueError:
        return JsonResponse({"error": "Invalid product id"}, status=400)

    if pid not in _product_store:
        return JsonResponse({"error": "Product not found"}, status=404)

    del _product_store[pid]
    return JsonResponse({"message": "Product deleted"}, status=200)
