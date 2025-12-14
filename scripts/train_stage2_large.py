"""
Stage 2 Training - Large Scale (800 iterations)
Generates ~3,000 high-diversity examples
"""

import sys
sys.path.insert(0, '..')

from train_stage2 import run_stage2_training

if __name__ == "__main__":
    print("Starting large-scale Stage 2 training (800 iterations)...")
    print("Estimated output: ~3,000 high-diversity examples")
    print("Estimated cost: ~$0.80")
    print("Estimated time: ~24 hours")
    print("After schema augmentation: ~12,000 examples\n")

    optimizer, metrics = run_stage2_training(
        num_iterations=800,
        candidates_per_iteration=5,
        reward_threshold=0.5,
        num_runs=3,
        timeout_seconds=10,
        output_dir="data/stage2"
    )

    print("\n" + "="*70)
    print("Stage 2 complete! Next steps:")
    print("="*70)
    print("1. Run schema augmentation:")
    print("   PYTHONPATH=. python3 scripts/augment_schemas.py")
    print("\n2. Combine all stages:")
    print("   PYTHONPATH=. python3 scripts/combine_stages.py")
    print("\n3. Export for fine-tuning:")
    print("   PYTHONPATH=. python3 scripts/analyze_training.py export")
    print("="*70 + "\n")
