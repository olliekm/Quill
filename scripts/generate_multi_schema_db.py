"""
Generate test database with multiple diverse schemas
Each schema represents a different domain with unique optimization patterns
"""

import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)


def create_ecommerce_schema(conn):
    """E-commerce: users + orders (current schema, keep for consistency)"""

    conn.execute('DROP TABLE IF EXISTS orders')
    conn.execute('DROP TABLE IF EXISTS users')

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
            order_date TEXT
        )
    ''')

    # Insert 10K users
    users = []
    for i in range(10000):
        users.append((
            i + 1,
            fake.name(),
            fake.email(),
            random.randint(18, 80),
            fake.city(),
            fake.date_between(start_date='-2y', end_date='today').isoformat()
        ))

    conn.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', users)

    # Insert 50K orders
    orders = []
    for i in range(50000):
        orders.append((
            i + 1,
            random.randint(1, 10000),
            fake.word(),
            round(random.uniform(10, 1000), 2),
            fake.date_between(start_date='-1y', end_date='today').isoformat()
        ))

    conn.executemany('INSERT INTO orders VALUES (?, ?, ?, ?, ?)', orders)
    print(f"✓ E-commerce: {len(users)} users, {len(orders)} orders")


def create_social_network_schema(conn):
    """Social network: posts + comments (3-table JOIN patterns)"""

    conn.execute('DROP TABLE IF EXISTS comments')
    conn.execute('DROP TABLE IF EXISTS posts')

    conn.execute('''
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            likes INTEGER,
            created_at TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            user_id INTEGER,
            text TEXT,
            created_at TEXT
        )
    ''')

    # Insert 20K posts
    posts = []
    for i in range(20000):
        posts.append((
            i + 1,
            random.randint(1, 10000),
            fake.sentence(nb_words=6),
            fake.text(max_nb_chars=200),
            random.randint(0, 1000),
            fake.date_time_between(start_date='-6m', end_date='now').isoformat()
        ))

    conn.executemany('INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)', posts)

    # Insert 100K comments
    comments = []
    for i in range(100000):
        comments.append((
            i + 1,
            random.randint(1, 20000),
            random.randint(1, 10000),
            fake.sentence(nb_words=12),
            fake.date_time_between(start_date='-6m', end_date='now').isoformat()
        ))

    conn.executemany('INSERT INTO comments VALUES (?, ?, ?, ?, ?)', comments)
    print(f"✓ Social network: {len(posts)} posts, {len(comments)} comments")


def create_hr_schema(conn):
    """HR system: employees with self-referencing manager relationship"""

    conn.execute('DROP TABLE IF EXISTS employees')

    conn.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            manager_id INTEGER,
            department TEXT,
            salary REAL,
            hire_date TEXT
        )
    ''')

    # Insert 5K employees with manager hierarchy
    employees = []
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']

    for i in range(5000):
        # First 50 are top-level (no manager)
        manager_id = None if i < 50 else random.randint(1, min(i, 500))

        employees.append((
            i + 1,
            fake.name(),
            fake.email(),
            manager_id,
            random.choice(departments),
            round(random.uniform(50000, 200000), 2),
            fake.date_between(start_date='-10y', end_date='today').isoformat()
        ))

    conn.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)', employees)
    print(f"✓ HR system: {len(employees)} employees (self-referencing)")


def create_analytics_schema(conn):
    """Analytics: events (time-series, aggregation-heavy)"""

    conn.execute('DROP TABLE IF EXISTS events')

    conn.execute('''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            event_type TEXT,
            properties TEXT,
            timestamp TEXT
        )
    ''')

    # Insert 200K events
    events = []
    event_types = ['page_view', 'click', 'signup', 'purchase', 'logout']

    for i in range(200000):
        events.append((
            i + 1,
            random.randint(1, 10000),
            random.choice(event_types),
            f'{{"page": "{fake.uri_path()}"}}',
            fake.date_time_between(start_date='-30d', end_date='now').isoformat()
        ))

    conn.executemany('INSERT INTO events VALUES (?, ?, ?, ?, ?)', events)
    print(f"✓ Analytics: {len(events)} events (time-series)")


def create_content_platform_schema(conn):
    """Content platform: articles + tags + junction table (many-to-many)"""

    conn.execute('DROP TABLE IF EXISTS article_tags')
    conn.execute('DROP TABLE IF EXISTS tags')
    conn.execute('DROP TABLE IF EXISTS articles')

    conn.execute('''
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY,
            author_id INTEGER,
            title TEXT,
            content TEXT,
            views INTEGER,
            published_at TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE tags (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')

    conn.execute('''
        CREATE TABLE article_tags (
            article_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (article_id, tag_id)
        )
    ''')

    # Insert 100 tags (ensure unique)
    tag_names = set()
    while len(tag_names) < 100:
        tag_names.add(fake.word())
    tags = [(i + 1, name) for i, name in enumerate(sorted(tag_names))]
    conn.executemany('INSERT INTO tags VALUES (?, ?)', tags)

    # Insert 10K articles
    articles = []
    for i in range(10000):
        articles.append((
            i + 1,
            random.randint(1, 1000),
            fake.sentence(nb_words=8),
            fake.text(max_nb_chars=500),
            random.randint(0, 100000),
            fake.date_between(start_date='-2y', end_date='today').isoformat()
        ))

    conn.executemany('INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?)', articles)

    # Insert article-tag relationships (avg 3 tags per article)
    article_tags = []
    for article_id in range(1, 10001):
        num_tags = random.randint(1, 5)
        tag_ids = random.sample(range(1, 101), num_tags)
        for tag_id in tag_ids:
            article_tags.append((article_id, tag_id))

    conn.executemany('INSERT INTO article_tags VALUES (?, ?)', article_tags)
    print(f"✓ Content platform: {len(articles)} articles, {len(tags)} tags, {len(article_tags)} relationships")


if __name__ == "__main__":
    print("Generating multi-schema test database...")
    print("=" * 70)

    conn = sqlite3.connect('data/test.db')

    create_ecommerce_schema(conn)
    create_social_network_schema(conn)
    create_hr_schema(conn)
    create_analytics_schema(conn)
    create_content_platform_schema(conn)

    conn.commit()
    conn.close()

    print("=" * 70)
    print("✅ Database created: data/test.db")
    print("\nSchemas available:")
    print("  1. E-commerce: users, orders")
    print("  2. Social network: posts, comments")
    print("  3. HR system: employees (self-join)")
    print("  4. Analytics: events (time-series)")
    print("  5. Content platform: articles, tags, article_tags (many-to-many)")
