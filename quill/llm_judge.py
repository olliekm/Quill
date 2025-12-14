"""
LLM-as-Judge for SQL query readability scoring
Uses preference comparison: which query is more readable?
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class SQLReadabilityJudge:
    def __init__(self, model="gpt-4o-mini", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def judge_readability(self, query_a: str, query_b: str, schema: str = "") -> dict:
        """
        Compare readability of two SQL queries.

        Returns:
            {
                "preference": "A" | "B" | "tie",
                "reasoning": str,
                "confidence": "high" | "medium" | "low"
            }
        """
        prompt = self._build_prompt(query_a, query_b, schema)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert SQL code reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def _build_prompt(self, query_a: str, query_b: str, schema: str) -> str:
        """Build the evaluation prompt for the LLM"""

        prompt = f"""You are an expert SQL code reviewer. Compare the readability of these two SQL queries that produce the same results.

Schema:
{schema}

Query A (Original):
{query_a}

Query B (Optimized):
{query_b}

Evaluate based on:
1. Clarity - Is the query easy to understand?
2. Maintainability - Would it be easy to modify later?
3. Best practices - Does it follow SQL conventions?
4. Complexity - Is it unnecessarily complex?

Respond in this exact JSON format:
{{
    "preference": "A" | "B" | "tie",
    "reasoning": "Brief explanation (1-2 sentences)",
    "confidence": "high" | "medium" | "low"
}}

If both queries are equally readable, return "tie".
If the optimized query (B) is more readable, return "B".
If the original query (A) is more readable despite being slower, return "A"."""

        return prompt

    def calculate_readability_bonus(self, preference: str, confidence: str) -> float:
        """
        Calculate readability bonus for reward function.

        Returns value between 0.0 and 0.2:
        - If optimized query (B) is more readable: +0.1 to +0.2
        - If tie: 0.0
        - If original (A) is more readable: -0.1 to -0.2 (penalty)
        """
        confidence_multiplier = {
            "high": 1.0,
            "medium": 0.75,
            "low": 0.5
        }

        base_bonus = {
            "B": 0.2,   # Optimized is more readable
            "tie": 0.0,  # Equal readability
            "A": -0.2   # Optimized is less readable (penalty)
        }

        multiplier = confidence_multiplier.get(confidence, 0.5)
        bonus = base_bonus.get(preference, 0.0)

        return bonus * multiplier


if __name__ == "__main__":
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

    print("Example usage:")
    print("Query A (simple):", query_a)
    print("Query B (with index):", query_b)
    print("\nLLM would judge which is more readable and maintainable")
    print("Then calculate readability bonus: -0.2 to +0.2")
