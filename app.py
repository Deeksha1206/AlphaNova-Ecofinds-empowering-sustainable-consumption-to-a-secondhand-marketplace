from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "ecofinds.db"

def query_db(query, args=()):
    conn = sqlite3.connect(DB_PATH)
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
    products = [
        {"id": r[0], "title": r[1], "description": r[2], "category": r[3], "price": r[4]}
        for r in rows
    ]
    return jsonify(products)

@app.route("/users")
def get_users():
    rows = query_db("SELECT id, email, username FROM users")
    users = [{"id": r[0], "email": r[1], "username": r[2]} for r in rows]
    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True)



  

