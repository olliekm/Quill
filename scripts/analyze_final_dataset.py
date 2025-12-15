"""
Analyze the final augmented dataset
"""

import json
from collections import Counter

def analyze_dataset(path):
    print("=" * 70)
    print(f"Analyzing Dataset: {path}")
    print("=" * 70)

    with open(path, 'r') as f:
        data = json.load(f)

    print(f"\n📊 Dataset Size: {len(data)} examples")

    # Unique queries
    unique_slow = len(set(ex.get('slow_query', '').strip() for ex in data))
    unique_fast = len(set(ex.get('fast_query', '').strip() for ex in data))

    print(f"\n🔍 Diversity:")
    print(f"  Unique slow queries: {unique_slow} ({unique_slow/len(data)*100:.1f}%)")
    print(f"  Unique fast queries: {unique_fast} ({unique_fast/len(data)*100:.1f}%)")

    # Optimization types
    opt_types = Counter(ex.get('optimization_type', 'unknown') for ex in data)

    print(f"\n🛠️  Optimization Types:")
    for opt_type, count in opt_types.most_common(10):
        print(f"  {opt_type}: {count} ({count/len(data)*100:.1f}%)")

    # Tables mentioned
    tables_mentioned = Counter()
    for ex in data:
        schema = ex.get('schema', '').lower()
        for table in ['users', 'orders', 'posts', 'comments', 'employees',
                      'events', 'articles', 'tags', 'customers', 'purchases',
                      'accounts', 'members', 'transactions', 'sales']:
            if table in schema:
                tables_mentioned[table] += 1

    print(f"\n📋 Tables Represented (top 10):")
    for table, count in tables_mentioned.most_common(10):
        print(f"  {table}: {count} examples")

    # Check for common patterns
    patterns = {
        'CREATE INDEX': 0,
        'JOIN': 0,
        'SELECT *': 0,
        'WHERE': 0,
        'GROUP BY': 0,
        'DISTINCT': 0
    }

    for ex in data:
        fast_query = ex.get('fast_query', '').upper()
        for pattern in patterns:
            if pattern in fast_query:
                patterns[pattern] += 1

    print(f"\n🔧 SQL Patterns in Optimized Queries:")
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern}: {count} ({count/len(data)*100:.1f}%)")

    # Check for complete examples
    complete = sum(1 for ex in data if all(k in ex for k in ['schema', 'slow_query', 'fast_query', 'explanation', 'optimization_type']))
    print(f"\n✅ Complete Examples: {complete}/{len(data)} ({complete/len(data)*100:.1f}%)")

    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "data/combined/training_data_augmented.json"

    analyze_dataset(path)
