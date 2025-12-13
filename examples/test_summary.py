import json
from quill.evaluator import SQLEvaluator

# Load seed data
with open('data/seed_data.json', 'r') as f:
    seed_data = json.load(f)

# Use the real test database
evaluator = SQLEvaluator(test_db_path="data/test.db")

print(f"Testing {len(seed_data)} examples with real data (10k users, 50k orders)...\n")

passed = 0
failed = 0
results = []

for i, example in enumerate(seed_data, 1):
    print(f"[{i}/20] Testing: {example['description'][:50]}...", end=" ")

    result = evaluator.evaluate_query(
        schema=example['schema'],
        original_query=example['slow_query'],
        optimized_query=example['fast_query'],
        num_runs=3,  # Reduced for speed
        timeout_seconds=10  # 10 second timeout per query
    )

    if result['success']:
        passed += 1
        speedup = result.get('speedup', 0)
        reward = result.get('reward', 0)
        timed_out = result.get('original_timed_out', False)
        timeout_marker = " (original timed out)" if timed_out else ""
        print(f"✅ {speedup:.2f}x speedup, reward: {reward:.2f}{timeout_marker}")
        results.append((i, example['description'], speedup, reward))
    else:
        failed += 1
        print(f"❌ {result.get('error', 'Unknown')}")

print(f"\n{'='*70}")
print(f"Summary: {passed} passed, {failed} failed out of {len(seed_data)} examples")
print(f"{'='*70}\n")

if results:
    print("Top performing optimizations:")
    results.sort(key=lambda x: x[2], reverse=True)
    for i, (num, desc, speedup, reward) in enumerate(results[:5], 1):
        print(f"{i}. Example #{num}: {speedup:.2f}x - {desc}")
