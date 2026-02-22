# Product APIs (in-memory)

Base URL: `http://127.0.0.1:8000/api/products/`

All create/update requests must use `Content-Type: application/json`.

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/products/create/` | Create a new product |
| GET | `/api/products/` | List all products |
| GET | `/api/products/<id>/` | Get one product by id |
| PUT | `/api/products/<id>/update/` | Full update |
| PATCH | `/api/products/<id>/update/` | Partial update |
| DELETE | `/api/products/<id>/delete/` | Delete a product |

## Request/Response

### Create product (POST)

**Body (JSON):**
- `name` (required): string
- `description` (optional): string, default `""`
- `category` (required): string
- `price` (required): number ≥ 0
- `brand` (required): string
- `quantity_in_warehouse` (optional): integer ≥ 0, default `0`

**Success:** `201` with product object (includes `id`).

### List products (GET)

**Success:** `200` with `{ "products": [...], "count": N }`.

### Get product (GET)

**Success:** `200` with product object. **404** if not found.

### Update product (PUT / PATCH)

**Body (JSON):** same fields as create; for PATCH only send fields to change.

**Success:** `200` with updated product. **404** if not found.

### Delete product (DELETE)

**Success:** `200` with `{ "message": "Product deleted" }`. **404** if not found.

## Validations

- Required fields must be present (create / full update).
- `price` must be ≥ 0.
- `quantity_in_warehouse` must be ≥ 0.
- Invalid JSON or unknown fields return `400`/`415` with error message.
