# API Documentation

Comprehensive technical reference for the **E-commerce Product REST API**.

- **Base URL (Local)**: `http://127.0.0.1:5000`
- **Interactive Swagger UI**: `http://127.0.0.1:5000/apidocs/`
- **OpenAPI 2.0 Spec (JSON)**: `http://127.0.0.1:5000/apispec_1.json` or local [swagger.json](file:///c:/Users/MYPC/Desktop/ecommerce-product-api/swagger.json)
- **Data Exchange Format**: `application/json`

---

## 1. HTTP Status Codes & Error Conventions

The API consistently communicates operation statuses using standard HTTP status codes. All errors return JSON objects with an `"error"` message.

| HTTP Code | Name | Scenario |
|:---|:---|:---|
| `200 OK` | Success | Successful GET, PUT, PATCH, or DELETE operation. |
| `201 Created` | Created | Resource successfully created via POST. |
| `400 Bad Request` | Client Error | Input validation failure, missing required fields, illegal values. |
| `404 Not Found` | Not Found | Requested product or category ID does not exist. |
| `405 Method Not Allowed` | Method Error | The HTTP method is not supported on the target URI. |
| `409 Conflict` | Conflict | Duplicate category name or deleting a category that has products. |
| `500 Server Error` | Server Error | Unhandled internal exception or database connection issue. |

### Standard Error Response Format

```json
{
  "error": "Category not found"
}
```

Or when multiple fields are missing:

```json
{
  "error": "Missing fields",
  "fields": ["name", "price", "stock", "category_id"]
}
```

---

## 2. Data Models & Relational Schema

### Category Model

Represents a logical product grouping (e.g., Electronics, Books).

| Field | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key, Auto-increment | Unique identifier |
| `name` | Text | Unique, Not Null, Trimmed | Category display name |
| `product_count` | Integer | Computed | Number of products in category (GET only) |

### Product Model

Represents an individual sellable item in the inventory.

| Field | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key, Auto-increment | Unique product identifier |
| `name` | Text | Not Null, Trimmed | Product title / name |
| `description` | Text | Optional, Default `""` | Detailed product description |
| `price` | Real (Float) | Not Null, `>= 0.0` | Item price in currency units |
| `stock` | Integer | Not Null, Default `0`, `>= 0` | Current quantity on hand |
| `category_id` | Integer | Foreign Key (`categories.id`), `ON DELETE RESTRICT` | Associated category ID |
| `category_name` | Text | Computed / Joined | Associated category name (GET only) |

---

## 3. General & System Endpoints

### 3.1 API Welcome & Discovery
- **Endpoint**: `GET /`
- **Description**: Returns API meta information and navigational hyperlinks.
- **Response `200 OK`**:
```json
{
  "name": "E-commerce Product REST API",
  "version": "1.0.0",
  "description": "RESTful API for managing products and categories with SQLite database storage.",
  "documentation": "/apidocs/",
  "health": "/api/health",
  "endpoints": {
    "products": {
      "list_or_create": "/api/products",
      "detail_update_delete": "/api/products/<product_id>"
    },
    "categories": {
      "list_or_create": "/api/categories",
      "detail_update_delete": "/api/categories/<category_id>"
    }
  }
}
```

### 3.2 System Health Check
- **Endpoint**: `GET /api/health`
- **Description**: Verifies API process liveliness and database connectivity.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 4. Categories Endpoints

### 4.1 List All Categories
- **Endpoint**: `GET /api/categories`
- **Description**: Returns all categories ordered by ID, including count of assigned products.
- **cURL Example**:
  ```bash
  curl -X GET http://127.0.0.1:5000/api/categories
  ```
- **Response `200 OK`**:
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "product_count": 5
  },
  {
    "id": 2,
    "name": "Clothing & Apparel",
    "product_count": 3
  }
]
```

### 4.2 Get Category by ID
- **Endpoint**: `GET /api/categories/{category_id}`
- **Parameters**: `category_id` (integer, path, required)
- **Response `200 OK`**:
```json
{
  "id": 1,
  "name": "Electronics",
  "product_count": 5
}
```
- **Response `404 Not Found`**:
```json
{
  "error": "Category not found"
}
```

### 4.3 Create a Category
- **Endpoint**: `POST /api/categories`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "name": "Home & Kitchen"
}
```
- **cURL Example**:
  ```bash
  curl -X POST http://127.0.0.1:5000/api/categories \
       -H "Content-Type: application/json" \
       -d '{"name": "Home & Kitchen"}'
  ```
- **Response `201 Created`**:
```json
{
  "message": "Category created successfully",
  "id": 3,
  "category": {
    "id": 3,
    "name": "Home & Kitchen"
  }
}
```
- **Response `409 Conflict` (Name already exists)**:
```json
{
  "error": "Category already exists"
}
```

### 4.4 Update a Category
- **Endpoint**: `PUT /api/categories/{category_id}`
- **Parameters**: `category_id` (integer, path, required)
- **Request Body**:
```json
{
  "name": "Home Decor & Kitchen"
}
```
- **Response `200 OK`**:
```json
{
  "message": "Category updated successfully",
  "category": {
    "id": 3,
    "name": "Home Decor & Kitchen"
  }
}
```

### 4.5 Delete a Category
- **Endpoint**: `DELETE /api/categories/{category_id}`
- **Parameters**: `category_id` (integer, path, required)
- **Constraint**: Deletion is blocked (`409 Conflict`) if products are currently assigned to this category.
- **cURL Example**:
  ```bash
  curl -X DELETE http://127.0.0.1:5000/api/categories/3
  ```
- **Response `200 OK`**:
```json
{
  "message": "Category deleted successfully"
}
```
- **Response `409 Conflict`**:
```json
{
  "error": "Cannot delete a category that has products"
}
```

---

## 5. Products Endpoints

### 5.1 List & Filter Products
- **Endpoint**: `GET /api/products`
- **Query Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `search` | String | No | Case-insensitive substring match on `name` or `description` |
  | `category_id` | Integer | No | Exact match filter by category ID |
  | `min_price` | Number | No | Filter items where `price >= min_price` |
  | `max_price` | Number | No | Filter items where `price <= max_price` |
  | `sort` | String | No | Sort order: `price_asc`, `price_desc`, `name_asc`, `name_desc`, `id_asc`, `id_desc` |

- **cURL Example**:
  ```bash
  curl -X GET "http://127.0.0.1:5000/api/products?search=wireless&min_price=20&sort=price_asc"
  ```

- **Response `200 OK`**:
```json
[
  {
    "id": 3,
    "name": "Ergonomic Wireless Mouse",
    "description": "Comfortable vertical wireless mouse with adjustable DPI.",
    "price": 39.99,
    "stock": 80,
    "category_id": 1,
    "category_name": "Electronics"
  },
  {
    "id": 1,
    "name": "Wireless Noise-Cancelling Headphones",
    "description": "Premium over-ear Bluetooth headphones with active noise cancellation.",
    "price": 129.99,
    "stock": 45,
    "category_id": 1,
    "category_name": "Electronics"
  }
]
```

### 5.2 Get Product by ID
- **Endpoint**: `GET /api/products/{product_id}`
- **Parameters**: `product_id` (integer, path, required)
- **cURL Example**:
  ```bash
  curl -X GET http://127.0.0.1:5000/api/products/1
  ```
- **Response `200 OK`**:
```json
{
  "id": 1,
  "name": "Wireless Noise-Cancelling Headphones",
  "description": "Premium over-ear Bluetooth headphones with active noise cancellation.",
  "price": 129.99,
  "stock": 45,
  "category_id": 1,
  "category_name": "Electronics"
}
```
- **Response `404 Not Found`**:
```json
{
  "error": "Product not found"
}
```

### 5.3 Create a Product
- **Endpoint**: `POST /api/products`
- **Headers**: `Content-Type: application/json`
- **Request Body Fields**:
  - `name` (String, required, non-empty)
  - `price` (Number, required, `>= 0`)
  - `category_id` (Integer, required, positive, must exist)
  - `stock` (Integer, optional, default `0`, `>= 0`)
  - `description` (String, optional, default `""`)

- **Request Body Example**:
```json
{
  "name": "Mechanical Gaming Keyboard",
  "description": "RGB tactile mechanical keyboard with detachable cable.",
  "price": 89.50,
  "stock": 30,
  "category_id": 1
}
```
- **cURL Example**:
  ```bash
  curl -X POST http://127.0.0.1:5000/api/products \
       -H "Content-Type: application/json" \
       -d '{
         "name": "Mechanical Gaming Keyboard",
         "description": "RGB tactile mechanical keyboard.",
         "price": 89.50,
         "stock": 30,
         "category_id": 1
       }'
  ```
- **Response `201 Created`**:
```json
{
  "message": "Product created successfully",
  "id": 2,
  "product": {
    "id": 2,
    "name": "Mechanical Gaming Keyboard",
    "description": "RGB tactile mechanical keyboard.",
    "price": 89.5,
    "stock": 30,
    "category_id": 1,
    "category_name": "Electronics"
  }
}
```
- **Response `400 Bad Request` (Invalid input)**:
```json
{
  "error": "Category not found"
}
```

### 5.4 Update a Product (Full Replacement)
- **Endpoint**: `PUT /api/products/{product_id}`
- **Parameters**: `product_id` (integer, path, required)
- **Request Body**:
```json
{
  "name": "Mechanical Gaming Keyboard RGB V2",
  "description": "Upgraded switches with sound dampening.",
  "price": 99.99,
  "stock": 25,
  "category_id": 1
}
```
- **Response `200 OK`**:
```json
{
  "message": "Product updated successfully"
}
```

### 5.5 Partially Update a Product (PATCH)
- **Endpoint**: `PATCH /api/products/{product_id}`
- **Parameters**: `product_id` (integer, path, required)
- **Description**: Updates only the fields provided in the body. Unspecified fields remain unchanged.
- **Request Body Example**:
```json
{
  "price": 79.99,
  "stock": 50
}
```
- **cURL Example**:
  ```bash
  curl -X PATCH http://127.0.0.1:5000/api/products/2 \
       -H "Content-Type: application/json" \
       -d '{"price": 79.99, "stock": 50}'
  ```
- **Response `200 OK`**:
```json
{
  "message": "Product updated successfully",
  "product": {
    "id": 2,
    "name": "Mechanical Gaming Keyboard",
    "description": "RGB tactile mechanical keyboard.",
    "price": 79.99,
    "stock": 50,
    "category_id": 1,
    "category_name": "Electronics"
  }
}
```

### 5.6 Delete a Product
- **Endpoint**: `DELETE /api/products/{product_id}`
- **Parameters**: `product_id` (integer, path, required)
- **cURL Example**:
  ```bash
  curl -X DELETE http://127.0.0.1:5000/api/products/2
  ```
- **Response `200 OK`**:
```json
{
  "message": "Product deleted successfully"
}
```
- **Response `404 Not Found`**:
```json
{
  "error": "Product not found"
}
```
