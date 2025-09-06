from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Database setup (pointing to your existing ecofinds.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecofinds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------
# Models (must match your DB schema)
# -----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(50), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(200), default="placeholder.png")

# -----------------------
# Routes
# -----------------------
@app.route("/")
def home():
    return "✅ Flask backend is connected to ecofinds.db"

# Get all products
@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "category": p.category,
        "price": p.price,
        "user_id": p.user_id,
        "image": p.image
    } for p in products])

# Get all users
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "email": u.email,
        "username": u.username
    } for u in users])

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    # IMPORTANT: Don't recreate tables, just use existing DB
    app.run(debug=True)

