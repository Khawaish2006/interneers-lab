"""
Controller layer — only handles HTTP request/response.
No business logic here. All logic lives in services.py.
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services import ProductService
from .schemas import CreateProductRequest, UpdateProductRequest, ProductResponse


def _parse_body(request):
    """Parse JSON body from request. Returns (data, error)."""
    try:
        return json.loads(request.body.decode("utf-8")), None
    except Exception:
        return None, JsonResponse({"error": "Invalid JSON body"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def product_create(request):
    data, err = _parse_body(request)
    if err:
        return err
    try:
        req = CreateProductRequest.from_dict(data)
        product = ProductService.create_product(req)
        return JsonResponse(ProductResponse.from_product(product).to_dict(), status=201)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def product_list(request):
    products = ProductService.get_all_products()
    return JsonResponse({
        "count": len(products),
        "products": [ProductResponse.from_product(p).to_dict() for p in products]
    })


@require_http_methods(["GET"])
def product_get(request, product_id):
    try:
        product = ProductService.get_product_by_id(product_id)
        return JsonResponse(ProductResponse.from_product(product).to_dict())
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=404)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def product_update(request, product_id):
    data, err = _parse_body(request)
    if err:
        return err
    try:
        partial = request.method == "PATCH"
        req = UpdateProductRequest.from_dict(data)
        product = ProductService.update_product(product_id, req, partial=partial)
        return JsonResponse(ProductResponse.from_product(product).to_dict())
    except ValueError as e:
        status = 404 if "not found" in str(e) else 400
        return JsonResponse({"error": str(e)}, status=status)


@csrf_exempt
@require_http_methods(["DELETE"])
def product_delete(request, product_id):
    try:
        ProductService.delete_product(product_id)
        return JsonResponse({"message": "Product deleted successfully"})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=404)