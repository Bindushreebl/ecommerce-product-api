# E-commerce Product REST API

A REST API built with Python, Flask, and SQLite.

## Features
- Create, retrieve, update, and delete products
- Create, retrieve, update, and delete categories
- SQLite database storage
- Product-category relationship

## Requirements
- Python 3
- Flask

## Setup
Install dependencies:

pip install -r requirements.txt

## Run the application

python app.py

The API runs at http://127.0.0.1:5000 by default.

## Product Endpoints
- GET /api/products
- POST /api/products
- GET /api/products/<product_id>
- PUT /api/products/<product_id>
- DELETE /api/products/<product_id>

## Category Endpoints
- GET /api/categories
- POST /api/categories
- PUT /api/categories/<category_id>
- DELETE /api/categories/<category_id>
