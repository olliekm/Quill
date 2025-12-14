"""
Quick training run for testing (5 iterations)
"""

import sys
sys.path.insert(0, '..')

from train_restem import run_training

if __name__ == "__main__":
    print("Running quick training test (5 iterations)...")
    optimizer, metrics = run_training(
        num_iterations=5,
        candidates_per_iteration=3,
        reward_threshold=0.5,
        num_runs=3,
        timeout_seconds=10,
        output_dir="data"
    )
