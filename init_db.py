import sqlite3

# connect to database (creates ecofinds.db if it doesn’t exist)
conn = sqlite3.connect("ecofinds.db")
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

CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);
""")

# Insert sample data
cursor.execute("INSERT OR IGNORE INTO users (email, username, password) VALUES (?,?,?)",
               ("alice@example.com", "Alice", "pass123"))
cursor.execute("INSERT OR IGNORE INTO users (email, username, password) VALUES (?,?,?)",
               ("bob@example.com", "Bob", "pass123"))

cursor.execute("INSERT OR IGNORE INTO products (title, description, category, price, user_id) VALUES (?,?,?,?,?)",
               ("Used Bicycle", "21-speed mountain bike, good condition", "Sports", 150.0, 1))
cursor.execute("INSERT OR IGNORE INTO products (title, description, category, price, user_id) VALUES (?,?,?,?,?)",
               ("Wooden Chair", "Solid wood chair with cushion", "Furniture", 45.0, 2))
cursor.execute("INSERT OR IGNORE INTO products (title, description, category, price, user_id) VALUES (?,?,?,?,?)",
               ("Data Structures Book", "Second-hand textbook", "Books", 10.0, 1))

conn.commit()
conn.close()
print("✅ Database ecofinds.db created with sample data")
