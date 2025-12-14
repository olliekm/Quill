"""
Test LLM judge for SQL readability
"""

import sys
sys.path.insert(0, '..')

from quill.llm_judge import SQLReadabilityJudge
import json

judge = SQLReadabilityJudge()

schema = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
);
"""

query_a = "SELECT * FROM users WHERE age > 30;"

query_b = """
CREATE INDEX IF NOT EXISTS idx_users_age ON users(age);
SELECT * FROM users WHERE age > 30;
"""

print("Testing LLM-as-Judge for SQL Readability")
print("="*60)
print(f"\nSchema:\n{schema}")
print(f"Query A (Original):\n{query_a}")
print(f"\nQuery B (Optimized):\n{query_b}")
print("\nCalling OpenAI to judge readability...")

try:
    result = judge.judge_readability(query_a, query_b, schema)

    print("\nJudge Result:")
    print(json.dumps(result, indent=2))

    preference = result.get("preference")
    reasoning = result.get("reasoning")
    confidence = result.get("confidence", "medium")

    bonus = judge.calculate_readability_bonus(preference, confidence)

    print(f"\nReadability Bonus: {bonus:+.2f}")
    print(f"Preference: Query {preference}")
    print(f"Reasoning: {reasoning}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure OPENAI_API_KEY is set in your .env file")
