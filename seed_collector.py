# seed_collector.py
import sqlite3
import time

# Create a test database
def create_test_db():
    conn = sqlite3.connect('data/test.db')

    # Drop existing tables to start fresh
    conn.execute('DROP TABLE IF EXISTS orders')
    conn.execute('DROP TABLE IF EXISTS users')

    # Create tables with realistic data
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            age INTEGER,
            city TEXT,
            signup_date TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product TEXT,
            amount REAL,
            order_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Insert 10k users
    import random
    from datetime import datetime, timedelta
    
    users = []
    for i in range(10000):
        users.append((
            i,
            f"User{i}",
            f"user{i}@example.com",
            random.randint(18, 80),
            random.choice(['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix']),
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        ))
    
    conn.executemany('INSERT INTO users VALUES (?,?,?,?,?,?)', users)
    
    # Insert 50k orders
    orders = []
    for i in range(50000):
        orders.append((
            i,
            random.randint(0, 9999),
            f"Product{random.randint(1, 100)}",
            random.uniform(10, 1000),
            (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d')
        ))
    
    conn.executemany('INSERT INTO orders VALUES (?,?,?,?,?)', orders)
    
    conn.commit()
    return conn

create_test_db()