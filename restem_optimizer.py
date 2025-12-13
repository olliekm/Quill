"""
ReSTEM (Reward-optimized Self-Training for Executable Models) SQL Optimizer
Self-improving loop: Generate → Evaluate → Filter → Add to training set → Iterate
"""

import json
from typing import List, Dict
from evaluator import SQLEvaluator


class ReSTEMOptimizer:
    def __init__(self, test_db_path="data/test.db", seed_data_path="data/seed_data.json", reward_threshold=0.5):
        self.evaluator = SQLEvaluator(test_db_path=test_db_path)
        self.seed_data_path = seed_data_path
        self.reward_threshold = reward_threshold
        self.training_examples = []
        self.successful_optimizations = []
        self._load_seed_data()

    def _load_seed_data(self):
        with open(self.seed_data_path, 'r') as f:
            self.training_examples = json.load(f)
        print(f"Loaded {len(self.training_examples)} seed examples")

    def generate_optimization(self, schema: str, slow_query: str) -> str:
        raise NotImplementedError("LLM integration needed. Add your LLM API call here.")

    def evaluate_and_filter(self, candidates: List[Dict], num_runs: int = 3, timeout_seconds: int = 10) -> List[Dict]:
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
        self.training_examples.extend(new_examples)
        self.successful_optimizations.extend(new_examples)
        print(f"Added {len(new_examples)} new examples (total: {len(self.training_examples)})")

    def save_training_data(self, output_path="data/augmented_training.json"):
        with open(output_path, 'w') as f:
            json.dump(self.training_examples, f, indent=2)
        print(f"Saved {len(self.training_examples)} examples to {output_path}")

    def get_stats(self) -> Dict:
        total = len(self.training_examples)
        by_type = {}

        for example in self.training_examples:
            opt_type = example.get('optimization_type', 'unknown')
            by_type[opt_type] = by_type.get(opt_type, 0) + 1

        avg_reward = 0
        if self.successful_optimizations:
            avg_reward = sum(e['reward'] for e in self.successful_optimizations) / len(self.successful_optimizations)

        return {
            'total_examples': total,
            'seed_examples': total - len(self.successful_optimizations),
            'generated_examples': len(self.successful_optimizations),
            'by_type': by_type,
            'avg_reward': avg_reward
        }

    def restem_iteration(self, num_candidates: int = 10, num_runs: int = 3, timeout_seconds: int = 10):
        print(f"\n{'='*70}")
        print(f"ReSTEM Iteration - Generating {num_candidates} candidates")
        print(f"{'='*70}\n")

        print("⚠️  LLM integration needed to generate candidates")
        candidates = []

        if not candidates:
            print("No candidates generated. Implement LLM integration first.")
            return 0

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

    print("\nTraining Statistics:")
    print(json.dumps(optimizer.get_stats(), indent=2))
