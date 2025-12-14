"""
Full ReSTEM training run (100 iterations)
Generates ~200+ examples for fine-tuning
Cost: ~$0.10
"""

import sys
sys.path.insert(0, '..')

from train_restem import run_training

if __name__ == "__main__":
    print("Starting full training run (100 iterations)...")
    print("Estimated cost: $0.10")
    print("Estimated time: ~80 minutes")
    print("Expected output: ~135 verified examples\n")

    optimizer, metrics = run_training(
        num_iterations=100,
        candidates_per_iteration=5,
        reward_threshold=0.5,
        num_runs=3,
        timeout_seconds=10,
        output_dir="data"
    )

    print("\n" + "="*70)
    print("Training complete! Next steps:")
    print("="*70)
    print("1. Analyze results:")
    print("   PYTHONPATH=. python3 scripts/analyze_training.py")
    print("\n2. Export for fine-tuning:")
    print("   PYTHONPATH=. python3 scripts/analyze_training.py export")
    print("="*70 + "\n")
