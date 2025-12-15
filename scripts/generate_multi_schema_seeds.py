"""
Generate seed data for multiple schemas
Each schema has 4-5 seed examples covering different optimization patterns
"""

import json

seed_data = []

# ============================================================================
# E-COMMERCE SCHEMA (users + orders)
# ============================================================================

seed_data.extend([
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
    {
        "id": 2,
        "description": "Correlated subquery to find users with high-value orders",
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
        "slow_query": "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_amount ON orders(amount);
SELECT DISTINCT u.* FROM users u JOIN orders o ON u.id = o.user_id WHERE o.amount > 100;
""",
        "explanation": "Replace correlated subquery with indexed JOIN",
        "optimization_type": "join"
    },
])

# ============================================================================
# SOCIAL NETWORK SCHEMA (posts + comments)
# ============================================================================

seed_data.extend([
    {
        "id": 10,
        "description": "Find posts with comment counts (subquery aggregation)",
        "schema": """
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    content TEXT,
    likes INTEGER,
    created_at TEXT
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER,
    user_id INTEGER,
    text TEXT,
    created_at TEXT
);
""",
        "slow_query": "SELECT *, (SELECT COUNT(*) FROM comments WHERE post_id = posts.id) as comment_count FROM posts;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
SELECT p.*, COUNT(c.id) as comment_count
FROM posts p
LEFT JOIN comments c ON p.id = c.post_id
GROUP BY p.id;
""",
        "explanation": "Replace correlated subquery with indexed JOIN and GROUP BY",
        "optimization_type": "join"
    },
    {
        "id": 11,
        "description": "Missing index on popular posts filter",
        "schema": """
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    content TEXT,
    likes INTEGER,
    created_at TEXT
);
""",
        "slow_query": "SELECT * FROM posts WHERE likes > 100 ORDER BY likes DESC LIMIT 10;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_posts_likes ON posts(likes DESC);
SELECT * FROM posts WHERE likes > 100 ORDER BY likes DESC LIMIT 10;
""",
        "explanation": "Index on likes column speeds up filtering and sorting",
        "optimization_type": "indexing"
    },
])

# ============================================================================
# HR SCHEMA (employees with self-join)
# ============================================================================

seed_data.extend([
    {
        "id": 20,
        "description": "Find employees and their managers (self-join)",
        "schema": """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    manager_id INTEGER,
    department TEXT,
    salary REAL,
    hire_date TEXT
);
""",
        "slow_query": "SELECT e.*, (SELECT name FROM employees WHERE id = e.manager_id) as manager_name FROM employees e;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_employees_manager_id ON employees(manager_id);
SELECT e.*, m.name as manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
""",
        "explanation": "Replace correlated subquery with self-join",
        "optimization_type": "join"
    },
    {
        "id": 21,
        "description": "Filter employees by department without index",
        "schema": """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    manager_id INTEGER,
    department TEXT,
    salary REAL,
    hire_date TEXT
);
""",
        "slow_query": "SELECT * FROM employees WHERE department = 'Engineering' AND salary > 100000;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_employees_dept_salary ON employees(department, salary);
SELECT * FROM employees WHERE department = 'Engineering' AND salary > 100000;
""",
        "explanation": "Composite index on department and salary speeds up multi-column filtering",
        "optimization_type": "indexing"
    },
])

# ============================================================================
# ANALYTICS SCHEMA (events - time-series)
# ============================================================================

seed_data.extend([
    {
        "id": 30,
        "description": "Count events by type without index",
        "schema": """
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    event_type TEXT,
    properties TEXT,
    timestamp TEXT
);
""",
        "slow_query": "SELECT event_type, COUNT(*) as count FROM events GROUP BY event_type;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
SELECT event_type, COUNT(*) as count FROM events GROUP BY event_type;
""",
        "explanation": "Index on event_type speeds up GROUP BY aggregation",
        "optimization_type": "indexing"
    },
    {
        "id": 31,
        "description": "Find users with recent activity (time-based filter)",
        "schema": """
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    event_type TEXT,
    properties TEXT,
    timestamp TEXT
);
""",
        "slow_query": "SELECT DISTINCT user_id FROM events WHERE timestamp > '2024-12-01' AND event_type = 'purchase';",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_events_type_time ON events(event_type, timestamp);
SELECT DISTINCT user_id FROM events WHERE event_type = 'purchase' AND timestamp > '2024-12-01';
""",
        "explanation": "Composite index on event_type and timestamp with optimized WHERE clause order",
        "optimization_type": "indexing"
    },
])

# ============================================================================
# CONTENT PLATFORM SCHEMA (articles + tags - many-to-many)
# ============================================================================

seed_data.extend([
    {
        "id": 40,
        "description": "Find articles by tag without index",
        "schema": """
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    author_id INTEGER,
    title TEXT,
    content TEXT,
    views INTEGER,
    published_at TEXT
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE article_tags (
    article_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (article_id, tag_id)
);
""",
        "slow_query": "SELECT a.* FROM articles a WHERE a.id IN (SELECT article_id FROM article_tags WHERE tag_id = 5);",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_article_tags_tag ON article_tags(tag_id);
SELECT DISTINCT a.* FROM articles a
JOIN article_tags at ON a.id = at.article_id
WHERE at.tag_id = 5;
""",
        "explanation": "Replace IN subquery with indexed JOIN for many-to-many relationship",
        "optimization_type": "join"
    },
    {
        "id": 41,
        "description": "Find popular articles with unnecessary SELECT *",
        "schema": """
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    author_id INTEGER,
    title TEXT,
    content TEXT,
    views INTEGER,
    published_at TEXT
);
""",
        "slow_query": "SELECT * FROM articles WHERE views > 1000 ORDER BY views DESC LIMIT 10;",
        "fast_query": """
CREATE INDEX IF NOT EXISTS idx_articles_views ON articles(views DESC);
SELECT id, title, views FROM articles WHERE views > 1000 ORDER BY views DESC LIMIT 10;
""",
        "explanation": "Index on views and select only needed columns instead of SELECT *",
        "optimization_type": "projection"
    },
])


# Save to file
output_path = "data/seed_data_multi_schema.json"
with open(output_path, 'w') as f:
    json.dump(seed_data, f, indent=2)

print(f"✅ Generated {len(seed_data)} seed examples across 5 schemas")
print(f"   Saved to: {output_path}")
print("\nBreakdown by schema:")
print(f"  - E-commerce: 2 examples")
print(f"  - Social network: 2 examples")
print(f"  - HR system: 2 examples")
print(f"  - Analytics: 2 examples")
print(f"  - Content platform: 2 examples")
