# seed_data.py
import json

seeds = [
    # 1. MISSING INDEX
    {
        "id": 1,
        "description": "Missing index on WHERE clause",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INTEGER,
    city TEXT,
    created_at TEXT
);
""",
        "slow_query": "SELECT * FROM users WHERE age > 30;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_age ON users(age);
SELECT * FROM users WHERE age > 30;
""",
        "explanation": "Added index on age column for faster filtering",
        "optimization_type": "indexing"
    },
    
    # 2. SELECT *
    {
        "id": 2,
        "description": "SELECT * wastes I/O bandwidth",
        "schema": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    price REAL,
    category TEXT,
    stock INTEGER,
    warehouse_location TEXT,
    supplier_info TEXT
);
""",
        "slow_query": "SELECT * FROM products WHERE category = 'electronics';",
        "fast_query": "SELECT id, name, price, stock FROM products WHERE category = 'electronics';",
        "explanation": "Only select columns you need to reduce I/O",
        "optimization_type": "projection"
    },
    
    # 3. SUBQUERY TO JOIN
    {
        "id": 3,
        "description": "IN subquery can be replaced with JOIN",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount REAL,
    status TEXT
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);
""",
        "slow_query": """
SELECT name, email FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);
""",
        "fast_query": """
SELECT DISTINCT u.name, u.email 
FROM users u 
INNER JOIN orders o ON u.id = o.user_id 
WHERE o.amount > 100;
""",
        "explanation": "JOIN is more efficient than IN with subquery",
        "optimization_type": "join"
    },
    
    # 4. NO LIMIT
    {
        "id": 4,
        "description": "Missing LIMIT on large table scan",
        "schema": """
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    level TEXT,
    message TEXT,
    user_id INTEGER
);
""",
        "slow_query": "SELECT * FROM logs ORDER BY timestamp DESC;",
        "fast_query": "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100;",
        "explanation": "Add LIMIT when you don't need all rows",
        "optimization_type": "limit"
    },
    
    # 5. MULTIPLE OR TO IN
    {
        "id": 5,
        "description": "Multiple OR conditions inefficient",
        "schema": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    category TEXT,
    price REAL,
    name TEXT
);
""",
        "slow_query": """
SELECT * FROM products 
WHERE category = 'electronics' 
   OR category = 'computers' 
   OR category = 'phones';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
SELECT * FROM products 
WHERE category IN ('electronics', 'computers', 'phones');
""",
        "explanation": "Use IN instead of multiple ORs and add index",
        "optimization_type": "indexing"
    },
    
    # 6. COMPOSITE INDEX
    {
        "id": 6,
        "description": "Missing composite index for multi-column filter",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    status TEXT,
    created_at TEXT,
    amount REAL
);
""",
        "slow_query": """
SELECT * FROM orders 
WHERE user_id = 123 AND status = 'pending';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_status ON orders(user_id, status);
SELECT * FROM orders 
WHERE user_id = 123 AND status = 'pending';
""",
        "explanation": "Composite index for multiple WHERE conditions",
        "optimization_type": "indexing"
    },
    
    # 7. FUNCTION IN WHERE
    {
        "id": 7,
        "description": "Function call in WHERE prevents index usage",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT,
    name TEXT,
    created_at TEXT
);
""",
        "slow_query": """
SELECT * FROM users 
WHERE LOWER(email) = 'test@example.com';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
SELECT * FROM users 
WHERE email = 'test@example.com';
""",
        "explanation": "Avoid functions in WHERE clause; store normalized data",
        "optimization_type": "indexing"
    },
    
    # 8. COUNT(*) VS EXISTS
    {
        "id": 8,
        "description": "COUNT when you only need to check existence",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount REAL
);
""",
        "slow_query": """
SELECT user_id, 
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
FROM users u
WHERE (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) > 0;
""",
        "fast_query": """
SELECT u.user_id, COUNT(o.id) as order_count
FROM users u
INNER JOIN orders o ON u.id = o.user_id
GROUP BY u.user_id;
""",
        "explanation": "Use JOIN and GROUP BY instead of correlated subqueries",
        "optimization_type": "join"
    },
    
    # 9. DISTINCT UNNECESSARY
    {
        "id": 9,
        "description": "DISTINCT when not needed",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE
);
""",
        "slow_query": "SELECT DISTINCT email FROM users;",
        "fast_query": "SELECT email FROM users;",
        "explanation": "DISTINCT is unnecessary when column is UNIQUE",
        "optimization_type": "redundancy"
    },
    
    # 10. NOT IN VS LEFT JOIN
    {
        "id": 10,
        "description": "NOT IN can be slow on large tables",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER
);
""",
        "slow_query": """
SELECT * FROM users 
WHERE id NOT IN (SELECT user_id FROM orders);
""",
        "fast_query": """
SELECT u.* FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.user_id IS NULL;
""",
        "explanation": "LEFT JOIN with NULL check faster than NOT IN",
        "optimization_type": "join"
    },
    
    # 11. ORDER BY WITHOUT INDEX
    {
        "id": 11,
        "description": "ORDER BY without supporting index",
        "schema": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL,
    created_at TEXT
);
""",
        "slow_query": """
SELECT * FROM products 
WHERE price > 50 
ORDER BY created_at DESC;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_products_price_created ON products(price, created_at DESC);
SELECT * FROM products 
WHERE price > 50 
ORDER BY created_at DESC;
""",
        "explanation": "Composite index covering both WHERE and ORDER BY",
        "optimization_type": "indexing"
    },
    
    # 12. LIKE WITH LEADING WILDCARD
    {
        "id": 12,
        "description": "LIKE with leading wildcard prevents index use",
        "schema": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    sku TEXT
);
""",
        "slow_query": """
SELECT * FROM products 
WHERE name LIKE '%laptop%';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
SELECT * FROM products 
WHERE name LIKE 'laptop%';
""",
        "explanation": "Avoid leading wildcards; use trailing wildcard with index",
        "optimization_type": "indexing"
    },
    
    # 13. UNNECESSARY SORTING
    {
        "id": 13,
        "description": "Sorting when order doesn't matter",
        "schema": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    score INTEGER
);
""",
        "slow_query": """
SELECT name, email FROM users 
WHERE score > 100 
ORDER BY name;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_score ON users(score);
SELECT name, email FROM users 
WHERE score > 100;
""",
        "explanation": "Remove ORDER BY if ordering isn't required",
        "optimization_type": "redundancy"
    },
    
    # 14. INEFFICIENT JOIN ORDER
    {
        "id": 14,
        "description": "Large table joined first",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount REAL
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    active INTEGER
);
""",
        "slow_query": """
SELECT o.* FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.active = 1;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
SELECT o.* FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.active = 1;
""",
        "explanation": "Filter smaller table first, add indexes",
        "optimization_type": "indexing"
    },
    
    # 15. AGGREGATION WITHOUT INDEX
    {
        "id": 15,
        "description": "GROUP BY without index",
        "schema": """
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    amount REAL,
    sale_date TEXT
);
""",
        "slow_query": """
SELECT product_id, SUM(amount) as total
FROM sales
GROUP BY product_id;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
SELECT product_id, SUM(amount) as total
FROM sales
GROUP BY product_id;
""",
        "explanation": "Index on GROUP BY column speeds up aggregation",
        "optimization_type": "indexing"
    },
    
    # 16. UNION VS UNION ALL
    {
        "id": 16,
        "description": "UNION when duplicates don't matter",
        "schema": """
CREATE TABLE active_users (
    id INTEGER PRIMARY KEY,
    name TEXT
);
CREATE TABLE inactive_users (
    id INTEGER PRIMARY KEY,
    name TEXT
);
""",
        "slow_query": """
SELECT name FROM active_users
UNION
SELECT name FROM inactive_users;
""",
        "fast_query": """
SELECT name FROM active_users
UNION ALL
SELECT name FROM inactive_users;
""",
        "explanation": "UNION ALL is faster when you don't need to remove duplicates",
        "optimization_type": "redundancy"
    },
    
    # 17. CORRELATED SUBQUERY
    {
        "id": 17,
        "description": "Correlated subquery in SELECT",
        "schema": """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    total REAL
);
""",
        "slow_query": """
SELECT 
    c.name,
    (SELECT SUM(total) FROM orders WHERE customer_id = c.id) as total_spent
FROM customers c;
""",
        "fast_query": """
SELECT 
    c.name,
    COALESCE(SUM(o.total), 0) as total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;
""",
        "explanation": "Replace correlated subquery with JOIN",
        "optimization_type": "join"
    },
    
    # 18. OFFSET PAGINATION
    {
        "id": 18,
        "description": "OFFSET pagination on large dataset",
        "schema": """
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    created_at TEXT
);
""",
        "slow_query": """
SELECT * FROM posts 
ORDER BY id 
LIMIT 20 OFFSET 10000;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_posts_id ON posts(id);
SELECT * FROM posts 
WHERE id > 10000 
ORDER BY id 
LIMIT 20;
""",
        "explanation": "Use WHERE with index instead of large OFFSET",
        "optimization_type": "indexing"
    },
    
    # 19. CASE IN WHERE
    {
        "id": 19,
        "description": "CASE statement in WHERE clause",
        "schema": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    category TEXT,
    price REAL,
    discount_price REAL
);
""",
        "slow_query": """
SELECT * FROM products
WHERE CASE 
    WHEN discount_price IS NOT NULL THEN discount_price 
    ELSE price 
END < 50;
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_discount ON products(discount_price);
SELECT * FROM products
WHERE (discount_price IS NOT NULL AND discount_price < 50)
   OR (discount_price IS NULL AND price < 50);
""",
        "explanation": "Expand CASE to separate conditions for index usage",
        "optimization_type": "indexing"
    },
    
    # 20. HAVING INSTEAD OF WHERE
    {
        "id": 20,
        "description": "Using HAVING when WHERE would work",
        "schema": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    status TEXT,
    amount REAL
);
""",
        "slow_query": """
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING status = 'completed';
""",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_status_user ON orders(status, user_id);
SELECT user_id, COUNT(*) as order_count
FROM orders
WHERE status = 'completed'
GROUP BY user_id;
""",
        "explanation": "Use WHERE to filter before grouping, not HAVING",
        "optimization_type": "indexing"
    }
]

# Save to file
with open('data/seed_data.json', 'w') as f:
    json.dump(seeds, f, indent=2)

print(f"✅ Created {len(seeds)} seed examples")
print("\nOptimization types:")
types = {}
for seed in seeds:
    opt_type = seed['optimization_type']
    types[opt_type] = types.get(opt_type, 0) + 1

for opt_type, count in sorted(types.items()):
    print(f"  - {opt_type}: {count}")