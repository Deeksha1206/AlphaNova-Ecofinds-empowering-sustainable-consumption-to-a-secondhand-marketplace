import sqlite3

DB_PATH = "ecofinds.db"

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
print("✅ Database initialized with sample data")

