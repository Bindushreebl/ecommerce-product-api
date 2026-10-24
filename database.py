
import os
import sqlite3

DEFAULT_DATABASE = "ecommerce.db"


def get_db_path(db_path=None):
    if db_path:
        return db_path
    if "VERCEL" in os.environ or "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
        return os.environ.get("DATABASE_PATH", "/tmp/ecommerce.db")
    return os.environ.get("DATABASE_PATH", DEFAULT_DATABASE)



def get_connection(db_path=None):
    target_db = get_db_path(db_path)
    connection = sqlite3.connect(target_db)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path=None):
    connection = get_connection(db_path)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                price REAL NOT NULL CHECK (price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id)
                    REFERENCES categories(id)
                    ON DELETE RESTRICT
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)
        """)

        connection.commit()
        print("Database tables created successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    init_db()

