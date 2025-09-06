from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "ecofinds.db"

# -----------------------
# Initialize DB and sample data
# -----------------------
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)

        # Insert sample users
        cursor.execute("INSERT OR IGNORE INTO users (email, username, password) VALUES (?,?,?)",
                       ("alice@example.com", "Alice", "pass123"))
        cursor.execute("INSERT OR IGNORE INTO users (email, username, password) VALUES (?,?,?)",
                       ("bob@example.com", "Bob", "pass123"))

        # Insert sample products
        cursor.execute("INSERT OR IGNORE INTO products (title, description, category, price, user_id) VALUES (?,?,?,?,?)",
                       ("Used Bicycle", "21-speed mountain bike, good condition", "Sports", 150.0, 1))
        cursor.execute("INSERT OR IGNORE INTO products (title, description, category, price, user_id) VALUES (?,?,?,?,?)",
                       ("Wooden Chair", "Solid wood chair with cushion", "Furniture", 45.0, 2))
        cursor.execute("INSERT OR IGNORE INTO products (title, description, category, price, user_id) VALUES (?,?,?,?,?)",
                       ("Data Structures Book", "Second-hand textbook", "Books", 10.0, 1))

        conn.commit()
        conn.close()
        print("✅ Database created and initialized with sample data")
    else:
        print("✅ Database already exists")

# -----------------------
# Utility function to query DB
# -----------------------
def query_db(query, args=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.close()
    return rows

# -----------------------
# Routes
# -----------------------
@app.route("/")
def home():
    return "✅ EcoFinds backend is running (SQLite direct)"

@app.route("/users")
def get_users():
    rows = query_db("SELECT id, email, username FROM users")
    users = [{"id": r[0], "email": r[1], "username": r[2]} for r in rows]
    return jsonify(users)

@app.route("/products")
def get_products():
    rows = query_db("SELECT id, title, description, category, price FROM products")
    products = [{"id": r[0], "title": r[1], "description": r[2], "category": r[3], "price": r[4]} for r in rows]
    return jsonify(products)

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)


  

