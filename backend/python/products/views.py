import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import ProductService
from .schemas import CreateProductRequest, UpdateProductRequest, ProductResponse


def _parse_body(request):
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
    sort = request.GET.get("sort", None)

    # collect filters from query params
    filters = {}
    if request.GET.get("category"):
        filters["category"] = request.GET.get("category")
    if request.GET.get("brand"):
        filters["brand"] = request.GET.get("brand")
    if request.GET.get("min_price"):
        filters["min_price"] = float(request.GET.get("min_price"))
    if request.GET.get("max_price"):
        filters["max_price"] = float(request.GET.get("max_price"))

    products = ProductService.get_all_products(sort=sort, filters=filters)
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


@require_http_methods(["GET"])
def recently_updated(request):
    days = int(request.GET.get("days", 7))
    products = ProductService.get_recently_updated(days=days)
    return JsonResponse({
        "count": len(products),
        "products": [ProductResponse.from_product(p).to_dict() for p in products]
    })


@csrf_exempt
@require_http_methods(["POST"])
def bulk_create(request):
    """Accept a CSV file and create multiple products"""
    try:
        # get the uploaded file
        csv_file = request.FILES.get("file")
        if not csv_file:
            return JsonResponse({"error": "No CSV file provided"}, status=400)

        csv_content = csv_file.read().decode("utf-8")
        results = ProductService.bulk_create_from_csv(csv_content)

        return JsonResponse({
            "created_count": len(results["created"]),
            "error_count": len(results["errors"]),
            "created": results["created"],
            "errors": results["errors"]
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)