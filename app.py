from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecofinds.db'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(50), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))
    price = db.Column(db.Float)
    image = db.Column(db.String(200))

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(email=data['email'], password=data['password'], username=data['username'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered!"})

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    product = Product(
        title=data['title'],
        description=data.get('description', ''),
        category=data.get('category', ''),
        price=data.get('price', 0),
        image=data.get('image', 'placeholder.png')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added!"})

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "category": p.category,
        "price": p.price,
        "image": p.image
    } for p in products])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
