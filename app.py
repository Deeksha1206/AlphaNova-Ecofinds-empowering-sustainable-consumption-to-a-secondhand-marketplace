from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)

# Use absolute path for DB
DB_PATH = os.path.join(os.path.dirname(__file__), "ecofinds.db")

# Helper function to query DB
def query_db(query, args=()):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)  # important for Flask
    conn.row_factory = sqlite3.Row  # allows dict-like access
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route("/")
def home():
    return "✅ EcoFinds backend is running (SQLite direct)"

@app.route("/products")
def get_products():
    rows = query_db("SELECT id, title, description, category, price FROM products")
    # Convert each row to dictionary
    products = [dict(r) for r in rows]
    return jsonify(products)

@app.route("/users")
def get_users():
    rows = query_db("SELECT id, email, username FROM users")
    users = [dict(r) for r in rows]
    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True)



  

