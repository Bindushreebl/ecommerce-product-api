"""
E-commerce Product REST API
A robust RESTful API built with Flask, SQLite, and Flasgger (OpenAPI/Swagger).
"""

from flask import Flask, request, jsonify
from flasgger import Swagger
from database import init_db, get_connection

app = Flask(__name__)

# ---------------- SWAGGER CONFIGURATION & TEMPLATE ----------------

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "E-commerce Product REST API",
        "description": "Production-ready RESTful API for managing e-commerce products and categories. Built with Flask, SQLite, and Flasgger.",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "url": "https://github.com/Bindushreebl/ecommerce-product-api"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "paths": {
        "/": {
            "get": {
                "tags": ["General"],
                "summary": "API Welcome and Discovery",
                "description": "Returns welcome message, API version, and links to all primary endpoints and documentation.",
                "responses": {
                    "200": {
                        "description": "API metadata and navigation links"
                    }
                }
            }
        },
        "/api/health": {
            "get": {
                "tags": ["General"],
                "summary": "Health Check",
                "description": "Returns the operational health status and database connectivity.",
                "responses": {
                    "200": {
                        "description": "API and database are healthy"
                    },
                    "500": {
                        "description": "Database connection error"
                    }
                }
            }
        },
        "/api/products": {
            "get": {
                "tags": ["Products"],
                "summary": "List all products",
                "description": "Retrieves products with optional filtering by search keyword, category, price range, and sorting.",
                "parameters": [
                    {
                        "name": "search",
                        "in": "query",
                        "type": "string",
                        "required": False,
                        "description": "Filter products by matching name or description"
                    },
                    {
                        "name": "category_id",
                        "in": "query",
                        "type": "integer",
                        "required": False,
                        "description": "Filter products by category ID"
                    },
                    {
                        "name": "min_price",
                        "in": "query",
                        "type": "number",
                        "required": False,
                        "description": "Minimum product price"
                    },
                    {
                        "name": "max_price",
                        "in": "query",
                        "type": "number",
                        "required": False,
                        "description": "Maximum product price"
                    },
                    {
                        "name": "sort",
                        "in": "query",
                        "type": "string",
                        "required": False,
                        "enum": ["id_asc", "id_desc", "price_asc", "price_desc", "name_asc", "name_desc"],
                        "description": "Sort order for products"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of products retrieved successfully"
                    },
                    "400": {
                        "description": "Invalid query parameters"
                    }
                }
            },
            "post": {
                "tags": ["Products"],
                "summary": "Create a new product",
                "description": "Creates a new product linked to an existing category.",
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
                                "description": {"type": "string", "example": "Ergonomic 2.4GHz optical mouse"},
                                "price": {"type": "number", "example": 29.99},
                                "stock": {"type": "integer", "example": 50},
                                "category_id": {"type": "integer", "example": 1}
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Product created successfully"
                    },
                    "400": {
                        "description": "Validation error or invalid category"
                    }
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
                    "description": "ID of the product"
                }
            ],
            "get": {
                "tags": ["Products"],
                "summary": "Get product by ID",
                "description": "Retrieves complete details of a product including its category name.",
                "responses": {
                    "200": {
                        "description": "Product retrieved successfully"
                    },
                    "404": {
                        "description": "Product not found"
                    }
                }
            },
            "put": {
                "tags": ["Products"],
                "summary": "Update a product (full replacement)",
                "description": "Replaces all product attributes. Requires name, price, stock, and category_id.",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name", "price", "stock", "category_id"],
                            "properties": {
                                "name": {"type": "string", "example": "Wireless Mouse Pro"},
                                "description": {"type": "string", "example": "Upgraded rechargeable wireless mouse"},
                                "price": {"type": "number", "example": 34.99},
                                "stock": {"type": "integer", "example": 40},
                                "category_id": {"type": "integer", "example": 1}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Product updated successfully"
                    },
                    "400": {
                        "description": "Validation error or category not found"
                    },
                    "404": {
                        "description": "Product not found"
                    }
                }
            },
            "patch": {
                "tags": ["Products"],
                "summary": "Partially update a product",
                "description": "Updates only specified fields of a product (e.g. price, stock, name).",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "example": "Wireless Mouse Pro"},
                                "description": {"type": "string", "example": "Updated description"},
                                "price": {"type": "number", "example": 27.99},
                                "stock": {"type": "integer", "example": 65},
                                "category_id": {"type": "integer", "example": 1}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Product updated successfully"
                    },
                    "400": {
                        "description": "Validation error"
                    },
                    "404": {
                        "description": "Product not found"
                    }
                }
            },
            "delete": {
                "tags": ["Products"],
                "summary": "Delete a product",
                "description": "Deletes the specified product from the catalog.",
                "responses": {
                    "200": {
                        "description": "Product deleted successfully"
                    },
                    "404": {
                        "description": "Product not found"
                    }
                }
            }
        },
        "/api/categories": {
            "get": {
                "tags": ["Categories"],
                "summary": "List all categories",
                "description": "Retrieves all product categories along with associated product counts.",
                "responses": {
                    "200": {
                        "description": "Categories retrieved successfully"
                    }
                }
            },
            "post": {
                "tags": ["Categories"],
                "summary": "Create a new category",
                "description": "Creates a unique product category.",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "example": "Home & Kitchen"}
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Category created successfully"
                    },
                    "400": {
                        "description": "Validation error"
                    },
                    "409": {
                        "description": "Category already exists"
                    }
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
                    "description": "ID of the category"
                }
            ],
            "get": {
                "tags": ["Categories"],
                "summary": "Get category by ID",
                "description": "Retrieves details of a single category and its product count.",
                "responses": {
                    "200": {
                        "description": "Category retrieved successfully"
                    },
                    "404": {
                        "description": "Category not found"
                    }
                }
            },
            "put": {
                "tags": ["Categories"],
                "summary": "Update a category",
                "description": "Updates category name. Name must remain unique.",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "example": "Home Decor & Kitchen"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Category updated successfully"
                    },
                    "400": {
                        "description": "Validation error"
                    },
                    "404": {
                        "description": "Category not found"
                    },
                    "409": {
                        "description": "Category name already exists"
                    }
                }
            },
            "delete": {
                "tags": ["Categories"],
                "summary": "Delete a category",
                "description": "Deletes an empty category. Deletion will be rejected if products are assigned to this category.",
                "responses": {
                    "200": {
                        "description": "Category deleted successfully"
                    },
                    "404": {
                        "description": "Category not found"
                    },
                    "409": {
                        "description": "Cannot delete category with associated products"
                    }
                }
            }
        }
    }
}

Swagger(app, config=swagger_config, template=swagger_template)

# Initialize database tables on startup
init_db()


# ---------------- ERROR HANDLERS (JSON ONLY) ----------------

@app.errorhandler(400)
def handle_bad_request(error):
    message = getattr(error, "description", "Bad request syntax or invalid parameters")
    return jsonify({"error": "Bad request", "message": str(message)}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def handle_internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ---------------- GENERAL & HEALTH ENDPOINTS ----------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
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
    }), 200


@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        connection = get_connection()
        connection.execute("SELECT 1").fetchone()
        connection.close()
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": f"connection failed: {str(e)}"
        }), 500


# ---------------- PRODUCTS ENDPOINTS ----------------

@app.route("/api/products", methods=["GET"])
def get_products():
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort = request.args.get("sort", "id_asc").lower().strip()

    connection = get_connection()
    try:
        query = """
            SELECT products.*, categories.name AS category_name
            FROM products
            JOIN categories ON products.category_id = categories.id
            WHERE (products.name LIKE ? OR products.description LIKE ?)
        """
        search_pattern = f"%{search}%"
        params = [search_pattern, search_pattern]

        if category_id is not None:
            try:
                cat_id_int = int(category_id)
                if cat_id_int <= 0:
                    return jsonify({"error": "category_id must be a positive integer"}), 400
            except ValueError:
                return jsonify({"error": "category_id must be an integer"}), 400

            query += " AND products.category_id = ?"
            params.append(cat_id_int)

        if min_price is not None:
            try:
                min_p = float(min_price)
                if min_p < 0:
                    return jsonify({"error": "min_price must be non-negative"}), 400
                query += " AND products.price >= ?"
                params.append(min_p)
            except ValueError:
                return jsonify({"error": "min_price must be a valid number"}), 400

        if max_price is not None:
            try:
                max_p = float(max_price)
                if max_p < 0:
                    return jsonify({"error": "max_price must be non-negative"}), 400
                query += " AND products.price <= ?"
                params.append(max_p)
            except ValueError:
                return jsonify({"error": "max_price must be a valid number"}), 400

        sort_mapping = {
            "id_asc": "products.id ASC",
            "id_desc": "products.id DESC",
            "price_asc": "products.price ASC",
            "price_desc": "products.price DESC",
            "name_asc": "products.name ASC",
            "name_desc": "products.name DESC",
        }
        order_clause = sort_mapping.get(sort, "products.id ASC")
        query += f" ORDER BY {order_clause}"

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
            "SELECT id, name FROM categories WHERE id = ?", (category_id,)
        ).fetchone()

        if category is None:
            return jsonify({"error": "Category not found"}), 400

        cursor = connection.execute("""
            INSERT INTO products (name, description, price, stock, category_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name.strip(), description.strip(), float(price), stock, category_id))
        connection.commit()

        new_id = cursor.lastrowid
        return jsonify({
            "message": "Product created successfully",
            "id": new_id,
            "product": {
                "id": new_id,
                "name": name.strip(),
                "description": description.strip(),
                "price": float(price),
                "stock": stock,
                "category_id": category_id,
                "category_name": category["name"]
            }
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
        """, (name.strip(), description.strip(), float(price), stock, category_id, product_id))
        connection.commit()

        return jsonify({"message": "Product updated successfully"}), 200
    finally:
        connection.close()


@app.route("/api/products/<int:product_id>", methods=["PATCH"])
def patch_product(product_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    allowed_fields = {"name", "description", "price", "stock", "category_id"}
    fields_to_update = {k: v for k, v in data.items() if k in allowed_fields}

    if not fields_to_update:
        return jsonify({"error": "No valid fields provided for update"}), 400

    connection = get_connection()
    try:
        existing = connection.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Product not found"}), 404

        updates = []
        params = []

        if "name" in fields_to_update:
            name = fields_to_update["name"]
            if not isinstance(name, str) or not name.strip():
                return jsonify({"error": "name cannot be empty"}), 400
            updates.append("name = ?")
            params.append(name.strip())

        if "description" in fields_to_update:
            desc = fields_to_update["description"]
            if not isinstance(desc, str):
                return jsonify({"error": "description must be text"}), 400
            updates.append("description = ?")
            params.append(desc.strip())

        if "price" in fields_to_update:
            price = fields_to_update["price"]
            if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
                return jsonify({"error": "price must be a non-negative number"}), 400
            updates.append("price = ?")
            params.append(float(price))

        if "stock" in fields_to_update:
            stock = fields_to_update["stock"]
            if type(stock) is not int or stock < 0:
                return jsonify({"error": "stock must be a non-negative integer"}), 400
            updates.append("stock = ?")
            params.append(stock)

        if "category_id" in fields_to_update:
            cat_id = fields_to_update["category_id"]
            if type(cat_id) is not int or cat_id <= 0:
                return jsonify({"error": "category_id must be a positive integer"}), 400
            cat_row = connection.execute(
                "SELECT id FROM categories WHERE id = ?", (cat_id,)
            ).fetchone()
            if cat_row is None:
                return jsonify({"error": "Category not found"}), 400
            updates.append("category_id = ?")
            params.append(cat_id)

        params.append(product_id)
        connection.execute(f"UPDATE products SET {', '.join(updates)} WHERE id = ?", params)
        connection.commit()

        updated_row = connection.execute("""
            SELECT products.*, categories.name AS category_name
            FROM products
            JOIN categories ON products.category_id = categories.id
            WHERE products.id = ?
        """, (product_id,)).fetchone()

        return jsonify({
            "message": "Product updated successfully",
            "product": dict(updated_row)
        }), 200
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


# ---------------- CATEGORIES ENDPOINTS ----------------

@app.route("/api/categories", methods=["GET"])
def get_categories():
    connection = get_connection()
    try:
        rows = connection.execute("""
            SELECT categories.id, categories.name, COUNT(products.id) AS product_count
            FROM categories
            LEFT JOIN products ON categories.id = products.category_id
            GROUP BY categories.id, categories.name
            ORDER BY categories.id
        """).fetchall()
        return jsonify([dict(row) for row in rows]), 200
    finally:
        connection.close()


@app.route("/api/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    connection = get_connection()
    try:
        row = connection.execute("""
            SELECT categories.id, categories.name, COUNT(products.id) AS product_count
            FROM categories
            LEFT JOIN products ON categories.id = products.category_id
            WHERE categories.id = ?
            GROUP BY categories.id, categories.name
        """, (category_id,)).fetchone()

        if row is None:
            return jsonify({"error": "Category not found"}), 404

        return jsonify(dict(row)), 200
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

    clean_name = name.strip()

    connection = get_connection()
    try:
        existing = connection.execute(
            "SELECT id FROM categories WHERE LOWER(name) = LOWER(?)", (clean_name,)
        ).fetchone()

        if existing:
            return jsonify({"error": "Category already exists"}), 409

        cursor = connection.execute(
            "INSERT INTO categories (name) VALUES (?)", (clean_name,)
        )
        connection.commit()

        return jsonify({
            "message": "Category created successfully",
            "id": cursor.lastrowid,
            "category": {
                "id": cursor.lastrowid,
                "name": clean_name
            }
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

    clean_name = name.strip()

    connection = get_connection()
    try:
        existing = connection.execute(
            "SELECT id FROM categories WHERE id = ?", (category_id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Category not found"}), 404

        duplicate = connection.execute(
            "SELECT id FROM categories WHERE LOWER(name) = LOWER(?) AND id != ?",
            (clean_name, category_id)
        ).fetchone()

        if duplicate:
            return jsonify({"error": "Category name already exists"}), 409

        connection.execute(
            "UPDATE categories SET name = ? WHERE id = ?",
            (clean_name, category_id)
        )
        connection.commit()

        return jsonify({
            "message": "Category updated successfully",
            "category": {
                "id": category_id,
                "name": clean_name
            }
        }), 200
    finally:
        connection.close()


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    connection = get_connection()
    try:
        # Check if category exists
        existing = connection.execute(
            "SELECT id FROM categories WHERE id = ?", (category_id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Category not found"}), 404

        # Check if any products reference this category
        prod_count = connection.execute(
            "SELECT COUNT(*) FROM products WHERE category_id = ?", (category_id,)
        ).fetchone()[0]

        if prod_count > 0:
            return jsonify({
                "error": "Cannot delete a category that has products"
            }), 409

        connection.execute(
            "DELETE FROM categories WHERE id = ?", (category_id,)
        )
        connection.commit()

        return jsonify({"message": "Category deleted successfully"}), 200
    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
