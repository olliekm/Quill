"""
Verify multi-schema database and seed data are set up correctly
Tests one example from each schema
"""

import sys
sys.path.insert(0, '.')

from quill.evaluator import SQLEvaluator
import json

print("=" * 70)
print("Multi-Schema Setup Verification")
print("=" * 70)

# Load seed data
with open('data/seed_data_multi_schema.json', 'r') as f:
    seeds = json.load(f)

print(f"\n✓ Loaded {len(seeds)} seed examples")

# Initialize evaluator
evaluator = SQLEvaluator(test_db_path='data/test.db')
print(f"✓ Initialized evaluator with database")

# Test one example from each schema
test_examples = {
    "E-commerce": seeds[0],
    "Social network": seeds[2],
    "HR system": seeds[4],
    "Analytics": seeds[6],
    "Content platform": seeds[8]
}

print("\n" + "=" * 70)
print("Testing Seed Examples")
print("=" * 70)

all_passed = True

for schema_name, example in test_examples.items():
    print(f"\n{schema_name}: {example['description']}")
    print("-" * 70)

    result = evaluator.evaluate_query(
        schema=example['schema'],
        original_query=example['slow_query'],
        optimized_query=example['fast_query'],
        num_runs=3,
        timeout_seconds=10
    )

    if result['success']:
        print(f"✅ Success!")
        print(f"   Speedup: {result['speedup']:.2f}x")
        print(f"   Reward: {result['reward']:.2f}")
        print(f"   Original time: {result['original_time']:.4f}s")
        print(f"   Optimized time: {result['optimized_time']:.4f}s")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print("✅ All schemas verified successfully!")
    print("\nReward distribution check:")

    rewards = []
    speedups = []

    for example in test_examples.values():
        result = evaluator.evaluate_query(
            schema=example['schema'],
            original_query=example['slow_query'],
            optimized_query=example['fast_query'],
            num_runs=1
        )
        if result['success']:
            rewards.append(result['reward'])
            speedups.append(result['speedup'])

    print(f"   Rewards range: {min(rewards):.2f} - {max(rewards):.2f}")
    print(f"   Speedups range: {min(speedups):.1f}x - {max(speedups):.1f}x")
    print(f"   Average reward: {sum(rewards)/len(rewards):.2f}")

    print("\n✅ Setup is ready for training!")
else:
    print("❌ Some schemas failed verification")
    print("   Please check the database and seed data")

print("=" * 70)
