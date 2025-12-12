# test_seed.py
from evaluator import SQLEvaluator
import json

with open('data/seed_data.json') as f:
    seeds = json.load(f)

evaluator = SQLEvaluator('data/test.db')

# Test seed #1
seed = seeds[0]
result = evaluator.evaluate_query(
    schema=seed['schema'],
    original_query=seed['slow_query'],
    optimized_query=seed['fast_query']
)

print(f"Seed #{seed['id']}: {seed['description']}")
print(f"Success: {result['success']}")
print(f"Speedup: {result.get('speedup', 0):.1f}x")
print(f"Reward: {result.get('reward', 0):.2f}")