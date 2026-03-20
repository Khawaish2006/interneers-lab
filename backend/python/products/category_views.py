# products/category_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .category_service import CategoryService


def _parse_body(request):
    try:
        return json.loads(request.body.decode("utf-8")), None
    except Exception:
        return None, JsonResponse({"error": "Invalid JSON body"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def category_create(request):
    data, err = _parse_body(request)
    if err:
        return err
    try:
        category = CategoryService.create_category(data)
        return JsonResponse(category.to_dict(), status=201)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def category_list(request):
    categories = CategoryService.get_all_categories()
    return JsonResponse({
        "count": len(categories),
        "categories": [c.to_dict() for c in categories]
    })


@require_http_methods(["GET"])
def category_get(request, category_id):
    try:
        category = CategoryService.get_category(category_id)
        return JsonResponse(category.to_dict())
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=404)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def category_update(request, category_id):
    data, err = _parse_body(request)
    if err:
        return err
    try:
        category = CategoryService.update_category(category_id, data)
        return JsonResponse(category.to_dict())
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def category_delete(request, category_id):
    try:
        CategoryService.delete_category(category_id)
        return JsonResponse({"message": "Category deleted successfully"})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=404)