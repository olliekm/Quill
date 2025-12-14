"""
ReSTEM (Reward-optimized Self-Training for Executable Models) SQL Optimizer
Self-improving loop: Generate → Evaluate → Filter → Add to training set → Iterate
"""

import json
import os
import random
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from quill.evaluator import SQLEvaluator

load_dotenv()


class ReSTEMOptimizer:
    def __init__(self, test_db_path="data/test.db", seed_data_path="data/seed_data.json",
                 reward_threshold=0.5, model="gpt-4o-mini"):
        self.evaluator = SQLEvaluator(test_db_path=test_db_path)
        self.seed_data_path = seed_data_path
        self.reward_threshold = reward_threshold
        self.training_examples = []
        self.successful_optimizations = []

        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self._load_seed_data()

    def _load_seed_data(self):
        with open(self.seed_data_path, 'r') as f:
            self.training_examples = json.load(f)
        print(f"Loaded {len(self.training_examples)} seed examples")

    def generate_optimization(self, schema: str, slow_query: str, num_examples: int = 3) -> dict:
        """
        Generate an optimized SQL query using LLM with few-shot examples.

        Returns:
            {
                "schema": str,
                "slow_query": str,
                "fast_query": str,
                "explanation": str,
                "optimization_type": str
            }
        """
        few_shot_examples = self._get_few_shot_examples(num_examples)
        prompt = self._build_optimization_prompt(schema, slow_query, few_shot_examples)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert SQL optimizer specializing in performance tuning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "schema": schema,
            "slow_query": slow_query,
            "fast_query": result.get("optimized_query"),
            "explanation": result.get("explanation"),
            "optimization_type": result.get("optimization_type", "unknown")
        }

    def _get_few_shot_examples(self, num_examples: int = 3) -> List[Dict]:
        """Sample random examples from training set for few-shot learning"""
        if len(self.training_examples) <= num_examples:
            return self.training_examples
        return random.sample(self.training_examples, num_examples)

    def _build_optimization_prompt(self, schema: str, slow_query: str, examples: List[Dict]) -> str:
        """Build prompt with few-shot examples for SQL optimization"""

        examples_text = ""
        for i, ex in enumerate(examples, 1):
            examples_text += f"""
Example {i}:
Schema: {ex['schema']}
Slow Query: {ex['slow_query']}
Optimized Query: {ex['fast_query']}
Explanation: {ex['explanation']}
Type: {ex['optimization_type']}
"""

        prompt = f"""You are optimizing SQL queries for performance. Learn from these examples:

{examples_text}

Now optimize this query:

Schema:
{schema}

Slow Query:
{slow_query}

Generate an optimized version of this query. Apply techniques like:
- Adding indexes (CREATE INDEX IF NOT EXISTS)
- Replacing subqueries with JOINs
- Using IN instead of multiple ORs
- Adding LIMIT when appropriate
- Composite indexes for multi-column filters
- Avoiding functions in WHERE clauses

Respond in this exact JSON format:
{{
    "optimized_query": "The optimized SQL query (can include CREATE INDEX statements before the SELECT)",
    "explanation": "Brief explanation of the optimization (1-2 sentences)",
    "optimization_type": "indexing|join|projection|limit|redundancy"
}}

Make sure the optimized query produces the same results as the original.
"""
        return prompt

    def evaluate_and_filter(self, candidates: List[Dict], num_runs: int = 3, timeout_seconds: int = 10) -> List[Dict]:
        """Evaluate candidates and filter by reward threshold"""
        successful = []

        for i, candidate in enumerate(candidates):
            print(f"[{i+1}/{len(candidates)}] Evaluating candidate...", end=" ")

            result = self.evaluator.evaluate_query(
                schema=candidate['schema'],
                original_query=candidate['slow_query'],
                optimized_query=candidate['fast_query'],
                num_runs=num_runs,
                timeout_seconds=timeout_seconds
            )

            if result['success'] and result['reward'] >= self.reward_threshold:
                speedup = result['speedup']
                reward = result['reward']
                print(f"✅ {speedup:.2f}x speedup, reward: {reward:.2f}")

                candidate['speedup'] = speedup
                candidate['reward'] = reward
                candidate['original_time'] = result['original_time']
                candidate['optimized_time'] = result['optimized_time']

                successful.append(candidate)
            else:
                error = result.get('error', 'Low reward')
                print(f"❌ {error}")

        return successful

    def augment_training_set(self, new_examples: List[Dict]):
        """Add successful optimizations to training set"""
        for example in new_examples:
            if 'id' not in example:
                example['id'] = len(self.training_examples) + 1
            if 'description' not in example:
                opt_type = example.get('optimization_type', 'optimization')
                example['description'] = f"Generated {opt_type} optimization"

        self.training_examples.extend(new_examples)
        self.successful_optimizations.extend(new_examples)
        print(f"Added {len(new_examples)} new examples (total: {len(self.training_examples)})")

    def save_training_data(self, output_path="data/augmented_training.json", clean_format=True):
        """Save augmented training data"""
        data_to_save = self.training_examples

        if clean_format:
            data_to_save = []
            for ex in self.training_examples:
                clean_ex = {
                    'id': ex.get('id'),
                    'description': ex.get('description'),
                    'schema': ex.get('schema'),
                    'slow_query': ex.get('slow_query'),
                    'fast_query': ex.get('fast_query'),
                    'explanation': ex.get('explanation'),
                    'optimization_type': ex.get('optimization_type')
                }
                data_to_save.append(clean_ex)

        with open(output_path, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        print(f"Saved {len(data_to_save)} examples to {output_path}")

    def get_stats(self) -> Dict:
        """Get training statistics"""
        total = len(self.training_examples)
        by_type = {}

        for example in self.training_examples:
            opt_type = example.get('optimization_type', 'unknown')
            by_type[opt_type] = by_type.get(opt_type, 0) + 1

        avg_reward = 0
        if self.successful_optimizations:
            avg_reward = sum(e.get('reward', 0) for e in self.successful_optimizations) / len(self.successful_optimizations)

        return {
            'total_examples': total,
            'seed_examples': total - len(self.successful_optimizations),
            'generated_examples': len(self.successful_optimizations),
            'by_type': by_type,
            'avg_reward': avg_reward
        }

    def restem_iteration(self, num_candidates: int = 5, num_runs: int = 3, timeout_seconds: int = 10):
        """
        Run one ReSTEM iteration:
        1. Generate candidate optimizations
        2. Evaluate and filter
        3. Add successful ones to training set
        """
        print(f"\n{'='*70}")
        print(f"ReSTEM Iteration - Generating {num_candidates} candidates")
        print(f"{'='*70}\n")

        candidates = []

        # Sample random slow queries from existing examples to create variations
        base_examples = random.sample(self.training_examples, min(num_candidates, len(self.training_examples)))

        for i, base in enumerate(base_examples):
            print(f"Generating candidate {i+1}/{num_candidates}...", end=" ")
            try:
                candidate = self.generate_optimization(
                    schema=base['schema'],
                    slow_query=base['slow_query']
                )
                candidates.append(candidate)
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")

        if not candidates:
            print("No candidates generated.")
            return 0

        print(f"\nGenerated {len(candidates)} candidates. Evaluating...\n")
        successful = self.evaluate_and_filter(candidates, num_runs, timeout_seconds)

        if successful:
            self.augment_training_set(successful)

        return len(successful)


if __name__ == "__main__":
    optimizer = ReSTEMOptimizer(
        test_db_path="data/test.db",
        seed_data_path="data/seed_data.json",
        reward_threshold=0.5
    )

    print("\nInitial Training Statistics:")
    print(json.dumps(optimizer.get_stats(), indent=2))

    # Run one iteration
    num_added = optimizer.restem_iteration(num_candidates=3)

    print(f"\n{'='*70}")
    print(f"Added {num_added} new high-quality examples")
    print(f"{'='*70}\n")

    print("Final Training Statistics:")
    print(json.dumps(optimizer.get_stats(), indent=2))

    # Save augmented data
    if num_added > 0:
        optimizer.save_training_data()
