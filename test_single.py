import json
import time
from evaluator import SQLEvaluator

# Load seed data
with open('data/seed_data.json', 'r') as f:
    seed_data = json.load(f)

evaluator = SQLEvaluator(test_db_path="data/test.db")

# Test example #7 specifically
example = seed_data[6]  # 0-indexed, so 6 = example 7

print(f"Testing Example #{example['id']}: {example['description']}")
print("\nThis query has correlated subqueries and will be VERY slow with 10k users...")
print("Let's test with a timeout...\n")

import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Query took too long!")

# Set a 30 second timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

try:
    result = evaluator.evaluate_query(
        schema=example['schema'],
        original_query=example['slow_query'],
        optimized_query=example['fast_query'],
        num_runs=1  # Just 1 run to test
    )
    signal.alarm(0)  # Cancel the alarm

    print(json.dumps(result, indent=2))
except TimeoutError:
    print("❌ Query timed out after 30 seconds!")
    print("\nThe slow_query does a correlated subquery for all 10k users.")
    print("This is O(n*m) complexity - extremely slow!")
