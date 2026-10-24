"""
Seed script to populate the e-commerce database with initial sample data.
Usage:
    python seed.py
"""

from database import init_db, get_connection


CATEGORIES = [
    {"name": "Electronics"},
    {"name": "Clothing & Apparel"},
    {"name": "Books & Stationery"},
    {"name": "Home & Kitchen"},
    {"name": "Sports & Outdoors"},
]

PRODUCTS = [
    {
        "name": "Wireless Noise-Cancelling Headphones",
        "description": "Premium over-ear Bluetooth headphones with active noise cancellation and 30-hour battery life.",
        "price": 129.99,
        "stock": 45,
        "category": "Electronics",
    },
    {
        "name": "Mechanical Gaming Keyboard",
        "description": "RGB backlit mechanical keyboard with tactile switches and detachable USB-C cable.",
        "price": 89.50,
        "stock": 30,
        "category": "Electronics",
    },
    {
        "name": "Ergonomic Wireless Mouse",
        "description": "Comfortable vertical wireless mouse with adjustable DPI and silent clicks.",
        "price": 39.99,
        "stock": 80,
        "category": "Electronics",
    },
    {
        "name": "4K Ultra HD Action Camera",
        "description": "Waterproof action camera with image stabilization, wide-angle lens, and dual screens.",
        "price": 199.00,
        "stock": 15,
        "category": "Electronics",
    },
    {
        "name": "USB-C Multiport Adapter Hub",
        "description": "7-in-1 USB-C hub with 4K HDMI, 3x USB 3.0, SD card reader, and 100W Power Delivery.",
        "price": 24.99,
        "stock": 120,
        "category": "Electronics",
    },
    {
        "name": "Classic Cotton Crewneck T-Shirt",
        "description": "100% breathable organic ring-spun cotton unisex daily wear t-shirt.",
        "price": 19.99,
        "stock": 200,
        "category": "Clothing & Apparel",
    },
    {
        "name": "Slim Fit Denim Jeans",
        "description": "Stretch denim jeans with tailored fit and reinforced double-stitched seams.",
        "price": 49.99,
        "stock": 75,
        "category": "Clothing & Apparel",
    },
    {
        "name": "Waterproof Windbreaker Jacket",
        "description": "Lightweight windproof and water-resistant hooded jacket with zip pockets.",
        "price": 79.99,
        "stock": 40,
        "category": "Clothing & Apparel",
    },
    {
        "name": "Clean Code: Agile Software Craftsmanship",
        "description": "Essential software engineering best practices guide by Robert C. Martin.",
        "price": 34.99,
        "stock": 50,
        "category": "Books & Stationery",
    },
    {
        "name": "Designing Data-Intensive Applications",
        "description": "Comprehensive guide to reliable, scalable, and maintainable data systems by Martin Kleppmann.",
        "price": 44.99,
        "stock": 65,
        "category": "Books & Stationery",
    },
    {
        "name": "Stainless Steel French Press Coffee Maker",
        "description": "Double-wall insulated 34-ounce French press with 4-level filtration system.",
        "price": 29.99,
        "stock": 60,
        "category": "Home & Kitchen",
    },
    {
        "name": "Non-Stick Ceramic Cookware Set",
        "description": "10-piece non-toxic ceramic non-stick pots and pans set with stay-cool handles.",
        "price": 119.00,
        "stock": 25,
        "category": "Home & Kitchen",
    },
    {
        "name": "Eco-Friendly Yoga Mat with Strap",
        "description": "High-density 6mm non-slip cushioned TPE yoga mat with carrying strap.",
        "price": 22.50,
        "stock": 90,
        "category": "Sports & Outdoors",
    },
    {
        "name": "Insulated Stainless Steel Water Bottle 32oz",
        "description": "Vacuum-insulated double-wall flask that keeps cold for 24 hours or hot for 12 hours.",
        "price": 18.99,
        "stock": 150,
        "category": "Sports & Outdoors",
    },
]


def seed_database(db_path=None):
    init_db(db_path)
    connection = get_connection(db_path)

    try:
        # Seed categories
        category_id_map = {}
        for cat in CATEGORIES:
            cursor = connection.execute(
                "SELECT id FROM categories WHERE name = ?", (cat["name"],)
            )
            row = cursor.fetchone()
            if row:
                category_id_map[cat["name"]] = row["id"]
            else:
                cursor = connection.execute(
                    "INSERT INTO categories (name) VALUES (?)", (cat["name"],)
                )
                category_id_map[cat["name"]] = cursor.lastrowid

        # Seed products
        seeded_count = 0
        for prod in PRODUCTS:
            cat_id = category_id_map[prod["category"]]
            existing = connection.execute(
                "SELECT id FROM products WHERE name = ?", (prod["name"],)
            ).fetchone()

            if not existing:
                connection.execute("""
                    INSERT INTO products (name, description, price, stock, category_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (prod["name"], prod["description"], prod["price"], prod["stock"], cat_id))
                seeded_count += 1

        connection.commit()
        print(f"Database seeded successfully! ({len(category_id_map)} categories, {seeded_count} new products added)")
    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()
