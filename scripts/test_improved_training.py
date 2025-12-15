"""
Test improved training setup with multi-schema and realistic rewards
Runs 2 iterations to verify everything works
"""

import sys
sys.path.insert(0, '.')

from scripts.train_stage2 import run_stage2_training

print("=" * 70)
print("Testing Improved Training Setup")
print("=" * 70)
print("Changes:")
print("  - Multi-schema database (5 domains)")
print("  - Reward threshold: 0.25 (accepts 2x+ speedups)")
print("  - Realistic reward scaling")
print("=" * 70 + "\n")

optimizer, metrics = run_stage2_training(
    num_iterations=2,
    candidates_per_iteration=3,
    reward_threshold=0.25,
    num_runs=2,
    timeout_seconds=10,
    output_dir="data/test_stage2"
)

print("\n" + "=" * 70)
print("Test Results")
print("=" * 70)

final_stats = metrics['final_stats']
print(f"Total examples: {final_stats['total_examples']}")
print(f"Unique queries: {final_stats['unique_slow_queries']}")
print(f"Diversity: {final_stats['diversity_ratio']:.1%}")
print(f"Average reward: {final_stats['avg_reward']:.2f}")
print(f"\nBy optimization type:")
for opt_type, count in final_stats['by_type'].items():
    print(f"  {opt_type}: {count}")

if metrics['summary']['total_successful'] > 0:
    print("\n✅ Test passed! Ready for full training.")
else:
    print("\n⚠️  No successful examples generated. Check reward threshold and queries.")

print("=" * 70)
