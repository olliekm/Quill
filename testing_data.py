import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('data/test.db')

# Users table
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        age INTEGER,
        city TEXT,
        created_at TEXT
    )
''')

users = [(i, f'User{i}', f'user{i}@test.com', random.randint(18, 70), 
          random.choice(['NYC', 'LA', 'Chicago']),
          (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat())
         for i in range(10000)]
conn.executemany('INSERT INTO users VALUES (?,?,?,?,?,?)', users)

# Orders table
conn.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        status TEXT,
        created_at TEXT
    )
''')

orders = [(i, random.randint(1, 9999), random.uniform(10, 500),
          random.choice(['pending', 'completed', 'cancelled']),
          (datetime.now() - timedelta(days=random.randint(0, 180))).isoformat())
         for i in range(50000)]
conn.executemany('INSERT INTO orders VALUES (?,?,?,?,?)', orders)

# Products table
conn.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL,
        stock INTEGER
    )
''')

products = [(i, f'Product{i}', 
            random.choice(['electronics', 'computers', 'phones', 'accessories']),
            random.uniform(10, 1000),
            random.randint(0, 100))
           for i in range(5000)]
conn.executemany('INSERT INTO products VALUES (?,?,?,?,?)', products)

conn.commit()
print('✅ Test database created with 10k users, 50k orders, 5k products')