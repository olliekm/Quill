"""
Example: Using SQL Evaluator with Readability Judging
"""

import json
from evaluator import SQLEvaluator

# Example 1: Without readability judging (speed only)
print("="*70)
print("Example 1: Speed-only evaluation")
print("="*70)

evaluator = SQLEvaluator(test_db_path="data/test.db", use_readability_judge=False)

result = evaluator.evaluate_query(
    schema="""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
);
""",
    original_query="SELECT * FROM users WHERE age > 30;",
    optimized_query="""
CREATE INDEX IF NOT EXISTS idx_users_age ON users(age);
SELECT * FROM users WHERE age > 30;
""",
    num_runs=3
)

print(json.dumps(result, indent=2))
print(f"\nReward based on speed only: {result['reward']:.3f}")


# Example 2: With readability judging
print("\n" + "="*70)
print("Example 2: Speed + Readability evaluation")
print("="*70)
print("⚠️  Requires LLM API integration in llm_judge.py")
print("Once integrated, this will:")
print("  1. Measure speedup (as before)")
print("  2. Ask LLM: 'Which query is more readable: A or B?'")
print("  3. Calculate final reward = speedup_reward + readability_bonus")
print("\nReadability bonus range: -0.2 to +0.2")
print("  - If optimized is MORE readable: +0.2")
print("  - If equally readable: 0.0")
print("  - If optimized is LESS readable: -0.2")

# Uncomment once LLM integration is done:
# evaluator_with_judge = SQLEvaluator(test_db_path="data/test.db", use_readability_judge=True)
# result_with_readability = evaluator_with_judge.evaluate_query(...)
# print(json.dumps(result_with_readability, indent=2))
