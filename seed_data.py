# seed_data.py
import json

seeds = [
    # 1. MISSING INDEX ON AGE
    {
        "id": 1,
        "description": "Missing index on users.age filter",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
""",
        "slow_query": "SELECT * FROM users WHERE age > 30;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_age ON users(age);
SELECT * FROM users WHERE age > 30;
""",
        "explanation": "Index on age column speeds up WHERE filtering",
        "optimization_type": "indexing"
    },
    
    # 2. SELECT * OPTIMIZATION
    {
        "id": 2,
        "description": "SELECT * when only few columns needed",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
""",
        "slow_query": "SELECT * FROM users WHERE city = 'NYC';",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
SELECT id, name, email FROM users WHERE city = 'NYC';
""",
        "explanation": "Select only needed columns and add index",
        "optimization_type": "projection"
    },
    
    # 3. SUBQUERY TO JOIN
    {
        "id": 3,
        "description": "IN subquery for finding users with orders",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT name, email FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_amount ON orders(amount);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
SELECT DISTINCT u.name, u.email 
FROM users u 
INNER JOIN orders o ON u.id = o.user_id 
WHERE o.amount > 100;
""",
        "explanation": "JOIN with indexes faster than IN subquery",
        "optimization_type": "join"
    },
    
    # 4. MISSING LIMIT ON ORDERS
    {
        "id": 4,
        "description": "Scanning all orders without LIMIT",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": "SELECT * FROM orders ORDER BY order_date DESC;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date DESC);
SELECT * FROM orders ORDER BY order_date DESC LIMIT 100;
""",
        "explanation": "Add LIMIT and index for ordered results",
        "optimization_type": "limit"
    },
    
    # 5. MULTIPLE OR ON CITY
    {
        "id": 5,
        "description": "Multiple OR conditions on city",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
""",
        "slow_query": """
SELECT * FROM users 
WHERE city = 'NYC' OR city = 'LA' OR city = 'Chicago';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
SELECT * FROM users 
WHERE city IN ('NYC', 'LA', 'Chicago');
""",
        "explanation": "IN clause with index faster than multiple ORs",
        "optimization_type": "indexing"
    },
    
    # 6. COMPOSITE INDEX FOR ORDERS
    {
        "id": 6,
        "description": "Filter on user_id and amount without index",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT * FROM orders 
WHERE user_id = 123 AND amount > 50;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_amount ON orders(user_id, amount);
SELECT * FROM orders 
WHERE user_id = 123 AND amount > 50;
""",
        "explanation": "Composite index on both filter columns",
        "optimization_type": "indexing"
    },
    
    # 7. COUNT VS EXISTS
    {
        "id": 7,
        "description": "Using COUNT when only need existence check",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT u.name, 
       (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as order_count
FROM users u
WHERE (SELECT COUNT(*) FROM orders WHERE user_id = u.id) > 0;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
SELECT u.name, COUNT(o.id) as order_count
FROM users u
INNER JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
""",
        "explanation": "JOIN with GROUP BY faster than correlated subqueries",
        "optimization_type": "join"
    },
    
    # 8. ORDER BY WITHOUT INDEX
    {
        "id": 8,
        "description": "ORDER BY age without supporting index",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
""",
        "slow_query": """
SELECT name, email FROM users 
WHERE city = 'NYC' 
ORDER BY age DESC;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_city_age ON users(city, age DESC);
SELECT name, email FROM users 
WHERE city = 'NYC' 
ORDER BY age DESC;
""",
        "explanation": "Composite index covering WHERE and ORDER BY",
        "optimization_type": "indexing"
    },
    
    # 9. AGGREGATION WITHOUT INDEX
    {
        "id": 9,
        "description": "GROUP BY product without index",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT product, SUM(amount) as total_sales
FROM orders
GROUP BY product;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product);
SELECT product, SUM(amount) as total_sales
FROM orders
GROUP BY product;
""",
        "explanation": "Index on GROUP BY column speeds up aggregation",
        "optimization_type": "indexing"
    },
    
    # 10. NOT IN VS LEFT JOIN
    {
        "id": 10,
        "description": "Find users without orders using NOT IN",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT * FROM users 
WHERE id NOT IN (SELECT user_id FROM orders);
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
SELECT u.* FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.user_id IS NULL;
""",
        "explanation": "LEFT JOIN with NULL check faster than NOT IN",
        "optimization_type": "join"
    },
    
    # 11. DATE RANGE WITHOUT INDEX
    {
        "id": 11,
        "description": "Date range query without index",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT * FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
SELECT * FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';
""",
        "explanation": "Index on date column for range queries",
        "optimization_type": "indexing"
    },
    
    # 12. CORRELATED SUBQUERY
    {
        "id": 12,
        "description": "Correlated subquery for total order amount",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT 
    name,
    (SELECT SUM(amount) FROM orders WHERE user_id = u.id) as total_spent
FROM users u;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
SELECT 
    u.name,
    COALESCE(SUM(o.amount), 0) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
""",
        "explanation": "Replace correlated subquery with JOIN and aggregation",
        "optimization_type": "join"
    },
    
    # 13. INEFFICIENT PAGINATION
    {
        "id": 13,
        "description": "Large OFFSET for pagination",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT * FROM orders 
ORDER BY id 
LIMIT 20 OFFSET 10000;
""",
        "fast_query": """
SELECT * FROM orders 
WHERE id > 10000 
ORDER BY id 
LIMIT 20;
""",
        "explanation": "Use WHERE with index instead of large OFFSET",
        "optimization_type": "indexing"
    },
    
    # 14. FILTER BEFORE JOIN
    {
        "id": 14,
        "description": "Join large tables without pre-filtering",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT o.* FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.city = 'NYC';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
SELECT o.* FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.city = 'NYC';
""",
        "explanation": "Add indexes and filter smaller table first",
        "optimization_type": "indexing"
    },
    
    # 15. HAVING VS WHERE
    {
        "id": 15,
        "description": "Using HAVING when WHERE would filter earlier",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING amount > 100;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_amount_user ON orders(amount, user_id);
SELECT user_id, COUNT(*) as order_count
FROM orders
WHERE amount > 100
GROUP BY user_id;
""",
        "explanation": "Use WHERE to filter before GROUP BY, not HAVING",
        "optimization_type": "indexing"
    },
    
    # 16. MULTIPLE AGGREGATIONS
    {
        "id": 16,
        "description": "Multiple aggregations with separate scans",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT 
    user_id,
    (SELECT COUNT(*) FROM orders o1 WHERE o1.user_id = o.user_id) as order_count,
    (SELECT SUM(amount) FROM orders o2 WHERE o2.user_id = o.user_id) as total_amount
FROM orders o
GROUP BY user_id;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
SELECT 
    user_id,
    COUNT(*) as order_count,
    SUM(amount) as total_amount
FROM orders
GROUP BY user_id;
""",
        "explanation": "Single GROUP BY faster than multiple subqueries",
        "optimization_type": "join"
    },
    
    # 17. FILTER ON COMPUTED COLUMN
    {
        "id": 17,
        "description": "Filter on computed age range",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
""",
        "slow_query": """
SELECT * FROM users 
WHERE age / 10 = 3;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_age ON users(age);
SELECT * FROM users 
WHERE age >= 30 AND age < 40;
""",
        "explanation": "Avoid functions in WHERE; use range with index",
        "optimization_type": "indexing"
    },
    
    # 18. HIGH-VALUE ORDERS BY CITY
    {
        "id": 18,
        "description": "Find high-value orders by city without indexes",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT u.city, o.amount, o.product
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.amount > 500
ORDER BY u.city, o.amount DESC;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_amount ON orders(amount);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
SELECT u.city, o.amount, o.product
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.amount > 500
ORDER BY u.city, o.amount DESC;
""",
        "explanation": "Add indexes on all join and filter columns",
        "optimization_type": "indexing"
    },
    
    # 19. RECENT USERS WITHOUT INDEX
    {
        "id": 19,
        "description": "Find recent signups without date index",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
""",
        "slow_query": """
SELECT name, email, signup_date FROM users 
WHERE signup_date >= '2024-01-01'
ORDER BY signup_date DESC;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_signup ON users(signup_date DESC);
SELECT name, email, signup_date FROM users 
WHERE signup_date >= '2024-01-01'
ORDER BY signup_date DESC;
""",
        "explanation": "Index on signup_date for filtering and sorting",
        "optimization_type": "indexing"
    },
    
    # 20. TOP SPENDERS
    {
        "id": 20,
        "description": "Find top spenders without optimization",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    signup_date TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
);
""",
        "slow_query": """
SELECT u.name, u.email, SUM(o.amount) as total
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, u.email
ORDER BY total DESC;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
SELECT u.name, u.email, SUM(o.amount) as total
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, u.email
ORDER BY total DESC
LIMIT 100;
""",
        "explanation": "Add index and LIMIT for top-N query",
        "optimization_type": "indexing"
    }
]

# Save to file
with open('data/seed_data.json', 'w') as f:
    json.dump(seeds, f, indent=2)

print(f"✅ Created {len(seeds)} seed examples for your test database")
print("\nOptimization breakdown:")
types = {}
for seed in seeds:
    opt_type = seed['optimization_type']
    types[opt_type] = types.get(opt_type, 0) + 1

for opt_type, count in sorted(types.items()):
    print(f"  - {opt_type}: {count}")

print("\nColumns used:")
print("  Users: id, name, email, age, city, signup_date")
print("  Orders: id, user_id, product, amount, order_date")