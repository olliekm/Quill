import json
from evaluator import SQLEvaluator

# Load seed data
with open('data/seed_data.json', 'r') as f:
    seed_data = json.load(f)

# Use the real test database with 10k users and 50k orders
evaluator = SQLEvaluator(test_db_path="data/test.db")

# Test all examples
test_cases = list(range(1, 21))  # All 20 examples

for case_id in test_cases:
    example = seed_data[case_id - 1]
    print(f"\n{'='*60}")
    print(f"Testing Example #{example['id']}: {example['description']}")
    print(f"{'='*60}")

    result = evaluator.evaluate_query(
        schema=example['schema'],
        original_query=example['slow_query'],
        optimized_query=example['fast_query'],
        num_runs=3
    )

    print(json.dumps(result, indent=2))

    if result['success']:
        print(f"✅ Success! Speedup: {result['speedup']:.2f}x, Reward: {result['reward']:.3f}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
