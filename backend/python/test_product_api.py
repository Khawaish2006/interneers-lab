"""
Test script for Product APIs using HTTP client (urllib).
Run with: python test_product_api.py
Start the server first: python manage.py runserver
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000/api/products"


def req(method, url, data=None):
    """Send request and return (status_code, body_dict)."""
    headers = {}
    if data is not None:
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req_obj = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req_obj) as r:
            body = r.read().decode()
            return r.status, json.loads(body) if body else {}
    except urllib.error.URLError as e:
        if "refused" in str(e).lower() or "10061" in str(e):
            print("\nConnection refused. Is the Django server running?")
            print("Start it in another terminal:  python manage.py runserver\n")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body) if body else {"error": str(e)}
        except json.JSONDecodeError:
            return e.code, {"error": str(e), "raw_response": body[:500]}


def test_create():
    print("1. CREATE product")
    status, body = req("POST", f"{BASE}/create/", {
        "name": "Test Widget",
        "description": "A nice widget",
        "category": "Electronics",
        "price": 29.99,
        "brand": "Acme",
        "quantity_in_warehouse": 100,
    })
    if status != 201:
        print(f"   FAILED: status={status}, body={body}")
        sys.exit(1)
    if "id" not in body or body["name"] != "Test Widget":
        print(f"   FAILED: unexpected body {body}")
        sys.exit(1)
    print("   OK -> id =", body["id"])
    return body["id"]


def test_list():
    print("2. LIST products")
    status, body = req("GET", f"{BASE}/")
    assert status == 200
    assert "products" in body and "count" in body
    print("   OK -> count =", body["count"])
    return body["products"]


def test_get(pid):
    print("3. GET product", pid)
    status, body = req("GET", f"{BASE}/{pid}/")
    assert status == 200
    assert body.get("id") == pid
    print("   OK ->", body.get("name"))


def test_update_full(pid):
    print("4. UPDATE (PUT) product", pid)
    status, body = req("PUT", f"{BASE}/{pid}/update/", {
        "name": "Updated Widget",
        "description": "Updated desc",
        "category": "Electronics",
        "price": "39.99",
        "brand": "Acme",
        "quantity_in_warehouse": 50,
    })
    assert status == 200
    assert body["name"] == "Updated Widget" and body["price"] == "39.99"
    print("   OK")


def test_update_patch(pid):
    print("5. UPDATE (PATCH) product", pid)
    status, body = req("PATCH", f"{BASE}/{pid}/update/", {"price": "19.99"})
    assert status == 200
    assert body["price"] == "19.99"
    print("   OK")


def test_validations():
    print("6. VALIDATIONS (expect 400)")
    # Missing required field
    status, body = req("POST", f"{BASE}/create/", {"name": "X"})
    assert status == 400
    print("   Missing required -> 400 OK")
    # Invalid price
    status, body = req("POST", f"{BASE}/create/", {
        "name": "X", "category": "Y", "price": -1, "brand": "Z",
    })
    assert status == 400
    print("   Negative price -> 400 OK")


def test_delete(pid):
    print("7. DELETE product", pid)
    status, body = req("DELETE", f"{BASE}/{pid}/delete/")
    assert status == 200
    print("   OK")
    # Get should 404
    status, _ = req("GET", f"{BASE}/{pid}/")
    assert status == 404
    print("   GET after delete -> 404 OK")


if __name__ == "__main__":
    print("Product API tests (ensure server is running: python manage.py runserver)\n")
    pid = test_create()
    test_list()
    test_get(pid)
    test_update_full(pid)
    test_update_patch(pid)
    test_validations()
    test_delete(pid)
    print("\nAll tests passed.")
