"""
Test that V2 actually generates diverse NEW slow queries
"""

import sys
sys.path.insert(0, '..')

from quill.restem_optimizer_v2 import ReSTEMOptimizerV2
import json

print("="*70)
print("Testing V2 Optimizer Diversity")
print("="*70)

optimizer = ReSTEMOptimizerV2(
    test_db_path="data/test.db",
    seed_data_path="data/seed_data.json",
    reward_threshold=0.5
)

print(f"\nInitial seed examples: {len(optimizer.training_examples)}")

# Run 3 iterations to generate examples
print("\nRunning 3 test iterations...")
for i in range(3):
    print(f"\n--- Iteration {i+1} ---")
    num_added = optimizer.restem_iteration(num_candidates=2)
    print(f"Added: {num_added}")

# Analyze diversity
stats = optimizer.get_stats()

print("\n" + "="*70)
print("Results")
print("="*70)
print(f"Total examples: {stats['total_examples']}")
print(f"Seed examples: {stats['seed_examples']}")
print(f"Generated examples: {stats['generated_examples']}")
print(f"Unique slow queries: {stats['unique_slow_queries']}")
print(f"Diversity ratio: {stats['diversity_ratio']:.1%}")

# Show some generated slow queries
print("\n" + "="*70)
print("Sample Generated Slow Queries")
print("="*70)

generated = optimizer.successful_optimizations[:5]  # First 5 generated
for i, ex in enumerate(generated, 1):
    print(f"\n{i}. {ex.get('slow_query', '')[:100]}...")

# Verify they're unique
unique_queries = set()
for ex in optimizer.training_examples:
    unique_queries.add(ex.get('slow_query', '').strip())

print(f"\n" + "="*70)
print(f"✅ Verification: {len(unique_queries)} unique queries out of {len(optimizer.training_examples)} total")
print(f"✅ Diversity: {len(unique_queries) / len(optimizer.training_examples):.1%}")
print("="*70)

if stats['diversity_ratio'] > 0.8:
    print("\n✅ HIGH DIVERSITY - V2 is working correctly!")
else:
    print(f"\n⚠️  LOW DIVERSITY ({stats['diversity_ratio']:.1%}) - Check implementation")
