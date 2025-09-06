import sqlite3

conn = sqlite3.connect("ecofinds.db")
cursor = conn.cursor()

print("Users:")
for row in cursor.execute("SELECT * FROM users;"):
    print(row)

print("\nProducts:")
for row in cursor.execute("SELECT * FROM products;"):
    print(row)

conn.close()
