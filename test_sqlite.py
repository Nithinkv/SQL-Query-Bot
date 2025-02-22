import sqlite3

conn = sqlite3.connect("combined.db")
cursor = conn.cursor()

# Check sales table
cursor.execute("SELECT * FROM sales LIMIT 5")
print("Sales data:", cursor.fetchall())

# Check orders table
cursor.execute("SELECT * FROM orders LIMIT 5")
print("Orders data:", cursor.fetchall())

conn.close()