from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import jwt
import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

CORS(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = 'ecofinds.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def close_db(error):
    close_db()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            g.current_user_id = current_user_id
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated

def get_user_by_id(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return dict(user) if user else None

# User Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'message': 'Username, email, and password are required'}), 400
        
        db = get_db()
        
        # Check if user already exists
        existing_user = db.execute(
            'SELECT id FROM users WHERE email = ? OR username = ?',
            (email, username)
        ).fetchone()
        
        if existing_user:
            return jsonify({'message': 'User with this email or username already exists'}), 409
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor = db.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        db.commit()
        
        user_id = cursor.lastrowid
        
        # Generate token
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

# User Profile Routes
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile():
    try:
        user = get_user_by_id(g.current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get profile', 'error': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        
        if not username or not email:
            return jsonify({'message': 'Username and email are required'}), 400
        
        db = get_db()
        
        # Check if username/email is taken by another user
        existing_user = db.execute(
            'SELECT id FROM users WHERE (email = ? OR username = ?) AND id != ?',
            (email, username, g.current_user_id)
        ).fetchone()
        
        if existing_user:
            return jsonify({'message': 'Username or email already taken'}), 409
        
        # Update user
        db.execute(
            'UPDATE users SET username = ?, email = ? WHERE id = ?',
            (username, email, g.current_user_id)
        )
        db.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500

# Product Routes
@app.route('/api/products', methods=['POST'])
@token_required
def create_product():
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        category = data.get('category')
        price = data.get('price')
        image_placeholder = data.get('image_placeholder', 'placeholder.jpg')
        
        if not all([title, description, category, price]):
            return jsonify({'message': 'Title, description, category, and price are required'}), 400
        
        db = get_db()
        cursor = db.execute(
            'INSERT INTO products (title, description, category, price, image_placeholder, user_id) VALUES (?, ?, ?, ?, ?, ?)',
            (title, description, category, float(price), image_placeholder, g.current_user_id)
        )
        db.commit()
        
        product_id = cursor.lastrowid
        
        return jsonify({
            'message': 'Product created successfully',
            'product': {
                'id': product_id,
                'title': title,
                'description': description,
                'category': category,
                'price': float(price),
                'image_placeholder': image_placeholder
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Failed to create product', 'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        db = get_db()
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = '''
            SELECT p.*, u.username 
            FROM products p 
            JOIN users u ON p.user_id = u.id 
            WHERE 1=1
        '''
        params = []
        
        if category:
            query += ' AND p.category = ?'
            params.append(category)
        
        if search:
            query += ' AND p.title LIKE ?'
            params.append(f'%{search}%')
        
        query += ' ORDER BY p.created_at DESC'
        
        products = db.execute(query, params).fetchall()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product['id'],
                'title': product['title'],
                'description': product['description'],
                'category': product['category'],
                'price': product['price'],
                'image_placeholder': product['image_placeholder'],
                'created_at': product['created_at'],
                'seller': product['username']
            })
        
        return jsonify({'products': products_list}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get products', 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        db = get_db()
        product = db.execute(
            '''SELECT p.*, u.username 
               FROM products p 
               JOIN users u ON p.user_id = u.id 
               WHERE p.id = ?''', 
            (product_id,)
        ).fetchone()
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify({
            'product': {
                'id': product['id'],
                'title': product['title'],
                'description': product['description'],
                'category': product['category'],
                'price': product['price'],
                'image_placeholder': product['image_placeholder'],
                'created_at': product['created_at'],
                'seller': product['username']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get product', 'error': str(e)}), 500

@app.route('/api/my-products', methods=['GET'])
@token_required
def get_my_products():
    try:
        db = get_db()
        products = db.execute(
            'SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC',
            (g.current_user_id,)
        ).fetchall()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product['id'],
                'title': product['title'],
                'description': product['description'],
                'category': product['category'],
                'price': product['price'],
                'image_placeholder': product['image_placeholder'],
                'created_at': product['created_at']
            })
        
        return jsonify({'products': products_list}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get products', 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(product_id):
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        category = data.get('category')
        price = data.get('price')
        image_placeholder = data.get('image_placeholder')
        
        db = get_db()
        
        # Check if product exists and belongs to user
        product = db.execute(
            'SELECT * FROM products WHERE id = ? AND user_id = ?',
            (product_id, g.current_user_id)
        ).fetchone()
        
        if not product:
            return jsonify({'message': 'Product not found or not authorized'}), 404
        
        # Update product
        db.execute(
            '''UPDATE products 
               SET title = ?, description = ?, category = ?, price = ?, image_placeholder = ? 
               WHERE id = ? AND user_id = ?''',
            (title, description, category, float(price), image_placeholder, product_id, g.current_user_id)
        )
        db.commit()
        
        return jsonify({'message': 'Product updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to update product', 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(product_id):
    try:
        db = get_db()
        
        # Check if product exists and belongs to user
        product = db.execute(
            'SELECT * FROM products WHERE id = ? AND user_id = ?',
            (product_id, g.current_user_id)
        ).fetchone()
        
        if not product:
            return jsonify({'message': 'Product not found or not authorized'}), 404
        
        # Delete product
        db.execute('DELETE FROM products WHERE id = ? AND user_id = ?', (product_id, g.current_user_id))
        db.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to delete product', 'error': str(e)}), 500

# Cart Routes
@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart():
    try:
        db = get_db()
        cart_items = db.execute(
            '''SELECT c.*, p.title, p.price, p.image_placeholder, u.username as seller
               FROM cart c
               JOIN products p ON c.product_id = p.id
               JOIN users u ON p.user_id = u.id
               WHERE c.user_id = ?''',
            (g.current_user_id,)
        ).fetchall()
        
        cart_list = []
        total = 0
        for item in cart_items:
            cart_list.append({
                'id': item['id'],
                'product_id': item['product_id'],
                'title': item['title'],
                'price': item['price'],
                'quantity': item['quantity'],
                'image_placeholder': item['image_placeholder'],
                'seller': item['seller'],
                'added_at': item['added_at']
            })
            total += item['price'] * item['quantity']
        
        return jsonify({'cart_items': cart_list, 'total': total}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get cart', 'error': str(e)}), 500

@app.route('/api/cart', methods=['POST'])
@token_required
def add_to_cart():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'message': 'Product ID is required'}), 400
        
        db = get_db()
        
        # Check if product exists
        product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check if item already in cart
        existing_item = db.execute(
            'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
            (g.current_user_id, product_id)
        ).fetchone()
        
        if existing_item:
            # Update quantity
            db.execute(
                'UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
                (quantity, g.current_user_id, product_id)
            )
        else:
            # Add new item
            db.execute(
                'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                (g.current_user_id, product_id, quantity)
            )
        
        db.commit()
        return jsonify({'message': 'Item added to cart successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to add to cart', 'error': str(e)}), 500

@app.route('/api/cart/<int:cart_id>', methods=['DELETE'])
@token_required
def remove_from_cart(cart_id):
    try:
        db = get_db()
        
        # Check if cart item exists and belongs to user
        cart_item = db.execute(
            'SELECT * FROM cart WHERE id = ? AND user_id = ?',
            (cart_id, g.current_user_id)
        ).fetchone()
        
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        
        # Delete cart item
        db.execute('DELETE FROM cart WHERE id = ? AND user_id = ?', (cart_id, g.current_user_id))
        db.commit()
        
        return jsonify({'message': 'Item removed from cart successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to remove from cart', 'error': str(e)}), 500

# Purchase Routes
@app.route('/api/purchase', methods=['POST'])
@token_required
def make_purchase():
    try:
        data = request.get_json()
        cart_items = data.get('cart_items', [])
        
        if not cart_items:
            return jsonify({'message': 'No items to purchase'}), 400
        
        db = get_db()
        
        # Create purchase records
        for item in cart_items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            # Get product details
            product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
            if not product:
                continue
            
            # Create purchase record
            db.execute(
                'INSERT INTO purchases (user_id, product_id, quantity, price, total) VALUES (?, ?, ?, ?, ?)',
                (g.current_user_id, product_id, quantity, product['price'], product['price'] * quantity)
            )
        
        # Clear cart
        db.execute('DELETE FROM cart WHERE user_id = ?', (g.current_user_id,))
        db.commit()
        
        return jsonify({'message': 'Purchase completed successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Purchase failed', 'error': str(e)}), 500

@app.route('/api/purchases', methods=['GET'])
@token_required
def get_purchases():
    try:
        db = get_db()
        purchases = db.execute(
            '''SELECT pr.*, p.title, p.image_placeholder, u.username as seller
               FROM purchases pr
               JOIN products p ON pr.product_id = p.id
               JOIN users u ON p.user_id = u.id
               WHERE pr.user_id = ?
               ORDER BY pr.purchased_at DESC''',
            (g.current_user_id,)
        ).fetchall()
        
        purchases_list = []
        for purchase in purchases:
            purchases_list.append({
                'id': purchase['id'],
                'product_id': purchase['product_id'],
                'title': purchase['title'],
                'quantity': purchase['quantity'],
                'price': purchase['price'],
                'total': purchase['total'],
                'image_placeholder': purchase['image_placeholder'],
                'seller': purchase['seller'],
                'purchased_at': purchase['purchased_at']
            })
        
        return jsonify({'purchases': purchases_list}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get purchases', 'error': str(e)}), 500

# Categories endpoint
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = [
        'Electronics', 'Clothing', 'Books', 'Home & Garden', 
        'Sports', 'Toys', 'Automotive', 'Health & Beauty', 
        'Food & Beverage', 'Other'
    ]
    return jsonify({'categories': categories}), 200

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

       
