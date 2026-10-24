"""
Automated test suite for E-commerce Product REST API.
Covers CRUD endpoints, input validation, foreign key constraints, error handling, and search/filter.
"""

import os
import tempfile
import pytest
from database import init_db


@pytest.fixture
def client():
    # Use a clean temporary SQLite database for each test run
    db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_PATH"] = temp_db_path
    init_db(temp_db_path)

    # Import app after setting DATABASE_PATH
    from app import app
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client

    # Cleanup temporary database
    os.close(db_fd)
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)


# ---------------- GENERAL & ERROR HANDLING TESTS ----------------

def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "name" in data
    assert "endpoints" in data
    assert "documentation" in data


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_404_json_error(client):
    response = client.get("/api/non-existent-route")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "Resource not found"}


def test_405_json_error(client):
    response = client.post("/api/health")
    assert response.status_code == 405
    data = response.get_json()
    assert data == {"error": "Method not allowed"}


# ---------------- CATEGORIES CRUD TESTS ----------------

def test_category_crud_lifecycle(client):
    # 1. List initially empty
    res = client.get("/api/categories")
    assert res.status_code == 200
    assert res.get_json() == []

    # 2. Create category
    res = client.post("/api/categories", json={"name": "Audio & Video"})
    assert res.status_code == 201
    created = res.get_json()
    assert "id" in created
    cat_id = created["id"]
    assert created["category"]["name"] == "Audio & Video"

    # 3. Read single category
    res = client.get(f"/api/categories/{cat_id}")
    assert res.status_code == 200
    cat_data = res.get_json()
    assert cat_data["id"] == cat_id
    assert cat_data["name"] == "Audio & Video"
    assert cat_data["product_count"] == 0

    # 4. Update category
    res = client.put(f"/api/categories/{cat_id}", json={"name": "Audio & Visual Gear"})
    assert res.status_code == 200
    assert res.get_json()["category"]["name"] == "Audio & Visual Gear"

    # Verify update
    res = client.get(f"/api/categories/{cat_id}")
    assert res.get_json()["name"] == "Audio & Visual Gear"

    # 5. Delete category
    res = client.delete(f"/api/categories/{cat_id}")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Category deleted successfully"

    # Verify deleted
    res = client.get(f"/api/categories/{cat_id}")
    assert res.status_code == 404


def test_category_validation(client):
    # Missing name
    res = client.post("/api/categories", json={})
    assert res.status_code == 400
    assert "name is required" in res.get_json()["error"]

    # Empty string name
    res = client.post("/api/categories", json={"name": "   "})
    assert res.status_code == 400

    # Non-string name
    res = client.post("/api/categories", json={"name": 12345})
    assert res.status_code == 400

    # Non-JSON body
    res = client.post("/api/categories", data="plain text", content_type="text/plain")
    assert res.status_code == 400

    # Duplicate category name (case-insensitive)
    client.post("/api/categories", json={"name": "Gaming"})
    res = client.post("/api/categories", json={"name": "gaming"})
    assert res.status_code == 409
    assert res.get_json()["error"] == "Category already exists"

    # Update non-existent category
    res = client.put("/api/categories/9999", json={"name": "New Name"})
    assert res.status_code == 404

    # Delete non-existent category
    res = client.delete("/api/categories/9999")
    assert res.status_code == 404


# ---------------- PRODUCTS CRUD TESTS ----------------

def test_product_crud_lifecycle(client):
    # Setup category
    cat_res = client.post("/api/categories", json={"name": "Computers"})
    cat_id = cat_res.get_json()["id"]

    # 1. Create product
    prod_payload = {
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical keyboard with red switches",
        "price": 89.99,
        "stock": 25,
        "category_id": cat_id
    }
    res = client.post("/api/products", json=prod_payload)
    assert res.status_code == 201
    prod_data = res.get_json()
    assert "id" in prod_data
    prod_id = prod_data["id"]
    assert prod_data["product"]["name"] == "Mechanical Keyboard"
    assert prod_data["product"]["price"] == 89.99
    assert prod_data["product"]["stock"] == 25
    assert prod_data["product"]["category_name"] == "Computers"

    # 2. Get single product
    res = client.get(f"/api/products/{prod_id}")
    assert res.status_code == 200
    item = res.get_json()
    assert item["id"] == prod_id
    assert item["name"] == "Mechanical Keyboard"
    assert item["category_name"] == "Computers"

    # 3. Full update (PUT)
    put_payload = {
        "name": "Wireless Mechanical Keyboard",
        "description": "Upgraded wireless Bluetooth mechanical keyboard",
        "price": 99.99,
        "stock": 15,
        "category_id": cat_id
    }
    res = client.put(f"/api/products/{prod_id}", json=put_payload)
    assert res.status_code == 200

    res = client.get(f"/api/products/{prod_id}")
    assert res.get_json()["name"] == "Wireless Mechanical Keyboard"
    assert res.get_json()["price"] == 99.99

    # 4. Partial update (PATCH)
    patch_payload = {"price": 79.99, "stock": 40}
    res = client.patch(f"/api/products/{prod_id}", json=patch_payload)
    assert res.status_code == 200
    patched_product = res.get_json()["product"]
    assert patched_product["price"] == 79.99
    assert patched_product["stock"] == 40
    assert patched_product["name"] == "Wireless Mechanical Keyboard"

    # 5. Delete product
    res = client.delete(f"/api/products/{prod_id}")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Product deleted successfully"

    # Verify deleted
    res = client.get(f"/api/products/{prod_id}")
    assert res.status_code == 404


def test_product_validation(client):
    # Create category first
    cat_res = client.post("/api/categories", json={"name": "Accessories"})
    cat_id = cat_res.get_json()["id"]

    # Missing name
    res = client.post("/api/products", json={"price": 10.0, "category_id": cat_id})
    assert res.status_code == 400
    assert res.get_json()["error"] == "name is required"

    # Missing price
    res = client.post("/api/products", json={"name": "Item", "category_id": cat_id})
    assert res.status_code == 400
    assert res.get_json()["error"] == "price must be a number"

    # Negative price
    res = client.post("/api/products", json={"name": "Item", "price": -5.0, "category_id": cat_id})
    assert res.status_code == 400
    assert res.get_json()["error"] == "price cannot be negative"

    # Negative stock
    res = client.post("/api/products", json={"name": "Item", "price": 10.0, "stock": -2, "category_id": cat_id})
    assert res.status_code == 400
    assert res.get_json()["error"] == "stock must be a non-negative integer"

    # Invalid category (non-existent)
    res = client.post("/api/products", json={"name": "Item", "price": 10.0, "category_id": 9999})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Category not found"

    # Non-integer category_id
    res = client.post("/api/products", json={"name": "Item", "price": 10.0, "category_id": "abc"})
    assert res.status_code == 400

    # Non-JSON payload
    res = client.post("/api/products", data="string", content_type="text/plain")
    assert res.status_code == 400

    # Create a valid product to test PUT/PATCH updates against
    valid_prod = client.post("/api/products", json={
        "name": "Base Item",
        "price": 15.0,
        "stock": 5,
        "category_id": cat_id
    }).get_json()
    valid_id = valid_prod["id"]

    # PUT with missing fields
    res = client.put(f"/api/products/{valid_id}", json={"name": "Incomplete"})
    assert res.status_code == 400
    assert "Missing fields" in res.get_json()["error"]

    # PATCH non-existent product
    res = client.patch("/api/products/9999", json={"price": 20.0})
    assert res.status_code == 404

    # PATCH with invalid field types
    res = client.patch(f"/api/products/{valid_id}", json={"price": -10.0})
    assert res.status_code == 400

    # PATCH with invalid stock
    res = client.patch(f"/api/products/{valid_id}", json={"stock": -1})
    assert res.status_code == 400

    # PATCH with non-existent category
    res = client.patch(f"/api/products/{valid_id}", json={"category_id": 9999})
    assert res.status_code == 400

    # PATCH with no valid fields
    res = client.patch(f"/api/products/{valid_id}", json={"unknown_key": "val"})
    assert res.status_code == 400



def test_foreign_key_delete_protection(client):
    # Create category and product
    cat = client.post("/api/categories", json={"name": "Smartphones"}).get_json()
    cat_id = cat["id"]
    prod = client.post("/api/products", json={
        "name": "Smartphone X",
        "price": 699.99,
        "stock": 10,
        "category_id": cat_id
    }).get_json()
    prod_id = prod["id"]

    # Attempt to delete category while product exists -> 409 Conflict
    res = client.delete(f"/api/categories/{cat_id}")
    assert res.status_code == 409
    assert "Cannot delete a category that has products" in res.get_json()["error"]

    # Delete product first
    del_prod = client.delete(f"/api/products/{prod_id}")
    assert del_prod.status_code == 200

    # Now category deletion succeeds
    del_cat = client.delete(f"/api/categories/{cat_id}")
    assert del_cat.status_code == 200


def test_product_filtering_and_sorting(client):
    cat1_id = client.post("/api/categories", json={"name": "Books"}).get_json()["id"]
    cat2_id = client.post("/api/categories", json={"name": "Games"}).get_json()["id"]

    client.post("/api/products", json={"name": "Python Guide", "price": 25.0, "category_id": cat1_id})
    client.post("/api/products", json={"name": "Flask Web Dev", "price": 40.0, "category_id": cat1_id})
    client.post("/api/products", json={"name": "Strategy Board Game", "price": 55.0, "category_id": cat2_id})

    # Search filter
    res = client.get("/api/products?search=Python")
    assert res.status_code == 200
    items = res.get_json()
    assert len(items) == 1
    assert items[0]["name"] == "Python Guide"

    # Category filter
    res = client.get(f"/api/products?category_id={cat2_id}")
    assert res.status_code == 200
    items = res.get_json()
    assert len(items) == 1
    assert items[0]["name"] == "Strategy Board Game"

    # Price range filter
    res = client.get("/api/products?min_price=30&max_price=50")
    assert res.status_code == 200
    items = res.get_json()
    assert len(items) == 1
    assert items[0]["name"] == "Flask Web Dev"

    # Sorting by price ascending
    res = client.get("/api/products?sort=price_asc")
    assert res.status_code == 200
    items = res.get_json()
    prices = [item["price"] for item in items]
    assert prices == sorted(prices)

    # Sorting by price descending
    res = client.get("/api/products?sort=price_desc")
    assert res.status_code == 200
    items = res.get_json()
    prices = [item["price"] for item in items]
    assert prices == sorted(prices, reverse=True)

    # Invalid query parameters
    assert client.get("/api/products?category_id=invalid").status_code == 400
    assert client.get("/api/products?min_price=-5").status_code == 400
    assert client.get("/api/products?max_price=abc").status_code == 400


def test_category_product_count_and_same_name_update(client):
    cat_res = client.post("/api/categories", json={"name": "Office Supplies"})
    cat_id = cat_res.get_json()["id"]

    # Initial count is 0
    cat_data = client.get(f"/api/categories/{cat_id}").get_json()
    assert cat_data["product_count"] == 0

    # Add 2 products
    client.post("/api/products", json={"name": "Stapler", "price": 8.5, "category_id": cat_id})
    client.post("/api/products", json={"name": "Paperclips", "price": 2.5, "category_id": cat_id})

    # Updated count is 2
    cat_data = client.get(f"/api/categories/{cat_id}").get_json()
    assert cat_data["product_count"] == 2

    # Updating category with the exact same name should succeed (not trigger 409)
    res = client.put(f"/api/categories/{cat_id}", json={"name": "Office Supplies"})
    assert res.status_code == 200
    assert res.get_json()["category"]["name"] == "Office Supplies"


def test_individual_patch_fields(client):
    cat = client.post("/api/categories", json={"name": "Hardware"}).get_json()
    cat2 = client.post("/api/categories", json={"name": "Networking"}).get_json()

    prod = client.post("/api/products", json={
        "name": "Router",
        "description": "Dual-band WiFi 6 router",
        "price": 80.0,
        "stock": 10,
        "category_id": cat["id"]
    }).get_json()
    prod_id = prod["id"]

    # Patch description only
    res = client.patch(f"/api/products/{prod_id}", json={"description": "Updated WiFi 6 router"})
    assert res.status_code == 200
    assert res.get_json()["product"]["description"] == "Updated WiFi 6 router"

    # Patch category only
    res = client.patch(f"/api/products/{prod_id}", json={"category_id": cat2["id"]})
    assert res.status_code == 200
    assert res.get_json()["product"]["category_id"] == cat2["id"]
    assert res.get_json()["product"]["category_name"] == "Networking"

