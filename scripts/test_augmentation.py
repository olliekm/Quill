"""
Test schema augmentation on a small sample
"""

import json
import sys
sys.path.insert(0, '..')

from augment_schemas import generate_variants

# Test example from Stage 1
test_example = {
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
}

print("="*70)
print("Schema Augmentation Test")
print("="*70)

print("\n📋 ORIGINAL EXAMPLE:")
print("-"*70)
print(f"Description: {test_example['description']}")
print(f"\nSchema:\n{test_example['schema']}")
print(f"Slow Query:\n{test_example['slow_query']}")
print(f"Fast Query:\n{test_example['fast_query']}")

# Generate 3 variants
for i in range(3):
    print(f"\n{'='*70}")
    print(f"🔄 VARIANT {i+1}")
    print("="*70)

    variant = generate_variants(test_example, i)

    print(f"Description: {variant['description']}")
    print(f"\nSchema:\n{variant['schema']}")
    print(f"Slow Query:\n{variant['slow_query']}")
    print(f"Fast Query:\n{variant['fast_query']}")

print("\n" + "="*70)
print("✅ Augmentation Test Complete!")
print("="*70)
print("\nVerify that:")
print("1. Table names changed (users → customers/employees/members)")
print("2. Column names changed (age → customer_age/employee_age/member_age)")
print("3. SQL syntax remains valid")
print("4. Index names updated accordingly")
