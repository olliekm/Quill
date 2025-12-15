"""
Combine Stage 1 and Stage 2 training data
"""

import json
import os

def combine_stages():
    print("=" * 70)
    print("Combining Stage 1 and Stage 2 Data")
    print("=" * 70)

    # Load Stage 1 data
    stage1_path = "data/stage1/training_data.json"
    stage2_path = "data/stage2/training_data.json"
    output_path = "data/combined/training_data.json"

    stage1_data = []
    stage2_data = []

    if os.path.exists(stage1_path):
        with open(stage1_path, 'r') as f:
            stage1_data = json.load(f)
        print(f"✓ Loaded Stage 1: {len(stage1_data)} examples")
    else:
        print(f"⚠️  Stage 1 data not found at {stage1_path}")

    if os.path.exists(stage2_path):
        with open(stage2_path, 'r') as f:
            stage2_data = json.load(f)
        print(f"✓ Loaded Stage 2: {len(stage2_data)} examples")
    else:
        print(f"❌ Stage 2 data not found at {stage2_path}")
        return

    # Combine data
    combined_data = stage1_data + stage2_data

    # Calculate statistics
    unique_slow_queries = len(set(ex.get('slow_query', '').strip() for ex in combined_data))
    diversity = unique_slow_queries / len(combined_data) if combined_data else 0

    # Count optimization types
    opt_types = {}
    for ex in combined_data:
        opt_type = ex.get('optimization_type', 'unknown')
        opt_types[opt_type] = opt_types.get(opt_type, 0) + 1

    print("\n" + "=" * 70)
    print("Combined Dataset Statistics")
    print("=" * 70)
    print(f"Total examples: {len(combined_data)}")
    print(f"  - From Stage 1: {len(stage1_data)}")
    print(f"  - From Stage 2: {len(stage2_data)}")
    print(f"\nUnique slow queries: {unique_slow_queries}")
    print(f"Diversity: {diversity:.1%}")
    print(f"\nOptimization types:")
    for opt_type, count in sorted(opt_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {opt_type}: {count}")

    # Save combined data
    os.makedirs("data/combined", exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(combined_data, f, indent=2)

    print(f"\n✅ Combined data saved to: {output_path}")
    print("=" * 70)

    return combined_data

if __name__ == "__main__":
    combine_stages()
