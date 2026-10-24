
from flask import Flask, request, jsonify
from flasgger import Swagger
from database import init_db, get_connection

app = Flask(__name__)

# ---------------- SWAGGER DOCUMENTATION ----------------

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "E-commerce Product REST API",
        "description": "REST API for managing products and categories",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["https", "http"],
    "paths": {
        "/": {
            "get": {
                "tags": ["Home"],
                "summary": "API welcome message",
                "responses": {
                    "200": {"description": "API information"}
                }
            }
        },
        "/api/products": {
            "get": {
                "tags": ["Products"],
                "summary": "Get all products",
                "parameters": [
                    {
                        "name": "search",
                        "in": "query",
                        "type": "string",
                        "required": False,
                        "description": "Search products by name"
                    },
                    {
                        "name": "category_id",
                        "in": "query",
                        "type": "integer",
                        "required": False,
                        "description": "Filter by category ID"
                    }
                ],
                "responses": {
                    "200": {"description": "Products retrieved successfully"},
                    "400": {"description": "Invalid category ID"}
                }
            },
            "post": {
                "tags": ["Products"],
                "summary": "Create a product",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name", "price", "category_id"],
                            "properties": {
                                "name": {"type": "string", "example": "Wireless Mouse"},
                                "description": {"type": "string", "example": "Test product"},
                                "price": {"type": "number", "example": 599},
                                "stock": {"type": "integer", "example": 10},
                                "category_id": {"type": "integer", "example": 1}
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {"description": "Product created successfully"},
                    "400": {"description": "Invalid input or category"}
                }
            }
        },
        "/api/products/{product_id}": {
            "parameters": [
                {
                    "name": "product_id",
                    "in": "path",
                    "type": "integer",
                    "required": True,
                    "description": "Product ID"
                }
            ],
            "get": {
                "tags": ["Products"],
                "summary": "Get a product by ID",
                "responses": {
                    "200": {"description": "Product retrieved successfully"},
                    "404": {"description": "Product not found"}
                }
            },
            "put": {
                "tags": ["Products"],
                "summary": "Update a product",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name", "price", "stock", "category_id"],
                            "properties": {
                                "name": {"type": "string", "example": "Wireless Mouse"},
                                "description": {"type": "string", "example": "Updated description"},
                                "price": {"type": "number", "example": 699},
                                "stock": {"type": "integer", "example": 15},
                                "category_id": {"type": "integer", "example": 1}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Product updated successfully"},
                    "400": {"description": "Invalid input"},
                    "404": {"description": "Product not found"}
                }
            },
            "delete": {
                "tags": ["Products"],
                "summary": "Delete a product",
                "responses": {
                    "200": {"description": "Product deleted successfully"},
                    "404": {"description": "Product not found"}
                }
            }
        },
        "/api/categories": {
            "get": {
                "tags": ["Categories"],
                "summary": "Get all categories",
                "responses": {
                    "200": {"description": "Categories retrieved successfully"}
                }
            },
            "post": {
                "tags": ["Categories"],
                "summary": "Create a category",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "example": "Electronics"}
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {"description": "Category created successfully"},
                    "400": {"description": "Invalid input"},
                    "409": {"description": "Category already exists"}
                }
            }
        },
        "/api/categories/{category_id}": {
            "parameters": [
                {
                    "name": "category_id",
                    "in": "path",
                    "type": "integer",
                    "required": True,
                    "description": "Category ID"
                }
            ],
            "put": {
                "tags": ["Categories"],
                "summary": "Update a category",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "example": "Accessories"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Category updated successfully"},
                    "404": {"description": "Category not found"},
                    "409": {"description": "Category name already exists"}
                }
            },
            "delete": {
                "tags": ["Categories"],
                "summary": "Delete a category",
                "responses": {
                    "200": {"description": "Category deleted successfully"},
                    "404": {"description": "Category not found"},
                    "409": {"description": "Category contains products"}
                }
            }
        }
    }
}

Swagger(app, template=swagger_template)

# Initialize database tables
init_db()


# ---------------- HOME ----------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the E-commerce Product API",
        "endpoints": {
            "products": "/api/products",
            "categories": "/api/categories",
            "documentation": "/apidocs/"
        }
    })


# ---------------- PRODUCTS ----------------

@app.route("/api/products", methods=["GET"])
def get_products():
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id")

    connection = get_connection()
    try:
        query = """
            SELECT products.*, categories.name AS category_name
            FROM products
            JOIN categories ON products.category_id = categories.id
            WHERE products.name LIKE ?
        """
        params = [f"%{search}%"]

        if category_id:
            try:
                category_id = int(category_id)
                if category_id <= 0:
                    return jsonify({"error": "category_id must be positive"}), 400
            except ValueError:
                return jsonify({"error": "category_id must be an integer"}), 400

            query += " AND products.category_id = ?"
            params.append(category_id)

        query += " ORDER BY products.id"
        rows = connection.execute(query, params).fetchall()
        return jsonify([dict(row) for row in rows]), 200
    finally:
        connection.close()


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    connection = get_connection()
    try:
        row = connection.execute("""
            SELECT products.*, categories.name AS category_name
            FROM products
            JOIN categories ON products.category_id = categories.id
            WHERE products.id = ?
        """, (product_id,)).fetchone()

        if row is None:
            return jsonify({"error": "Product not found"}), 404

        return jsonify(dict(row)), 200
    finally:
        connection.close()


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock", 0)
    category_id = data.get("category_id")
    description = data.get("description", "")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required"}), 400

    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return jsonify({"error": "price must be a number"}), 400
    if price < 0:
        return jsonify({"error": "price cannot be negative"}), 400

    if type(stock) is not int or stock < 0:
        return jsonify({"error": "stock must be a non-negative integer"}), 400

    if type(category_id) is not int or category_id <= 0:
        return jsonify({"error": "category_id must be a positive integer"}), 400

    if not isinstance(description, str):
        return jsonify({"error": "description must be text"}), 400

    connection = get_connection()
    try:
        category = connection.execute(
            "SELECT id FROM categories WHERE id = ?", (category_id,)
        ).fetchone()

        if category is None:
            return jsonify({"error": "Category not found"}), 400

        cursor = connection.execute("""
            INSERT INTO products (name, description, price, stock, category_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name.strip(), description.strip(), price, stock, category_id))
        connection.commit()

        return jsonify({
            "message": "Product created successfully",
            "id": cursor.lastrowid
        }), 201
    finally:
        connection.close()


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    required = ["name", "price", "stock", "category_id"]
    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400

    name = data["name"]
    price = data["price"]
    stock = data["stock"]
    category_id = data["category_id"]
    description = data.get("description", "")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required"}), 400
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
        return jsonify({"error": "price must be a non-negative number"}), 400
    if type(stock) is not int or stock < 0:
        return jsonify({"error": "stock must be a non-negative integer"}), 400
    if type(category_id) is not int or category_id <= 0:
        return jsonify({"error": "category_id must be a positive integer"}), 400
    if not isinstance(description, str):
        return jsonify({"error": "description must be text"}), 400

    connection = get_connection()
    try:
        existing = connection.execute(
            "SELECT id FROM products WHERE id = ?", (product_id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Product not found"}), 404

        category = connection.execute(
            "SELECT id FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if category is None:
            return jsonify({"error": "Category not found"}), 400

        connection.execute("""
            UPDATE products
            SET name = ?, description = ?, price = ?, stock = ?, category_id = ?
            WHERE id = ?
        """, (name.strip(), description.strip(), price, stock, category_id, product_id))
        connection.commit()

        return jsonify({"message": "Product updated successfully"}), 200
    finally:
        connection.close()


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    connection = get_connection()
    try:
        cursor = connection.execute(
            "DELETE FROM products WHERE id = ?", (product_id,)
        )
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"message": "Product deleted successfully"}), 200
    finally:
        connection.close()


# ---------------- CATEGORIES ----------------

@app.route("/api/categories", methods=["GET"])
def get_categories():
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT * FROM categories ORDER BY id"
        ).fetchall()
        return jsonify([dict(row) for row in rows]), 200
    finally:
        connection.close()


@app.route("/api/categories", methods=["POST"])
def create_category():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required"}), 400

    connection = get_connection()
    try:
        existing = connection.execute(
            "SELECT id FROM categories WHERE name = ?", (name.strip(),)
        ).fetchone()

        if existing:
            return jsonify({"error": "Category already exists"}), 409

        cursor = connection.execute(
            "INSERT INTO categories (name) VALUES (?)", (name.strip(),)
        )
        connection.commit()

        return jsonify({
            "message": "Category created successfully",
            "id": cursor.lastrowid
        }), 201
    finally:
        connection.close()


@app.route("/api/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required"}), 400

    connection = get_connection()
    try:
        existing = connection.execute(
            "SELECT id FROM categories WHERE id = ?", (category_id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Category not found"}), 404

        duplicate = connection.execute(
            "SELECT id FROM categories WHERE name = ? AND id != ?",
            (name.strip(), category_id)
        ).fetchone()

        if duplicate:
            return jsonify({"error": "Category name already exists"}), 409

        connection.execute(
            "UPDATE categories SET name = ? WHERE id = ?",
            (name.strip(), category_id)
        )
        connection.commit()

        return jsonify({"message": "Category updated successfully"}), 200
    finally:
        connection.close()


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    connection = get_connection()
    try:
        cursor = connection.execute(
            "DELETE FROM categories WHERE id = ?", (category_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Category not found"}), 404

        connection.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception:
        connection.rollback()
        return jsonify({
            "error": "Cannot delete a category that has products"
        }), 409
    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True)
