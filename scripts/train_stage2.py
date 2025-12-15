"""
Stage 2 Training - High Diversity Data Generation
Generates NEW slow queries for each iteration
"""

import sys
sys.path.insert(0, '..')

import json
import time
from datetime import datetime
from quill.restem_optimizer_v2 import ReSTEMOptimizerV2


def run_stage2_training(
    num_iterations=100,
    candidates_per_iteration=5,
    reward_threshold=0.5,
    num_runs=3,
    timeout_seconds=10,
    output_dir="data/stage2"
):
    """
    Run Stage 2 ReSTEM training with high diversity
    """

    print(f"\n{'='*70}")
    print(f"ReSTEM Stage 2 Training - High Diversity")
    print(f"{'='*70}")
    print(f"Iterations: {num_iterations}")
    print(f"Candidates per iteration: {candidates_per_iteration}")
    print(f"Reward threshold: {reward_threshold}")
    print(f"KEY DIFFERENCE: Generates NEW slow queries each iteration")
    print(f"{'='*70}\n")

    optimizer = ReSTEMOptimizerV2(
        test_db_path="data/test.db",
        seed_data_path="data/seed_data_multi_schema.json",
        reward_threshold=reward_threshold
    )

    metrics = {
        'start_time': datetime.now().isoformat(),
        'stage': 2,
        'config': {
            'num_iterations': num_iterations,
            'candidates_per_iteration': candidates_per_iteration,
            'reward_threshold': reward_threshold,
            'num_runs': num_runs,
            'timeout_seconds': timeout_seconds
        },
        'iterations': [],
        'initial_stats': optimizer.get_stats()
    }

    print("Initial Training Set:")
    print(json.dumps(metrics['initial_stats'], indent=2))
    print()

    total_generated = 0
    total_candidates = 0
    start_time = time.time()

    for i in range(num_iterations):
        iteration_start = time.time()

        num_added = optimizer.restem_iteration(
            num_candidates=candidates_per_iteration,
            num_runs=num_runs,
            timeout_seconds=timeout_seconds
        )

        iteration_time = time.time() - iteration_start
        total_generated += num_added
        total_candidates += candidates_per_iteration
        success_rate = num_added / candidates_per_iteration if candidates_per_iteration > 0 else 0

        current_stats = optimizer.get_stats()

        iteration_metrics = {
            'iteration': i + 1,
            'candidates_generated': candidates_per_iteration,
            'successful': num_added,
            'success_rate': success_rate,
            'time_seconds': iteration_time,
            'total_examples': current_stats['total_examples'],
            'unique_slow_queries': current_stats['unique_slow_queries'],
            'diversity_ratio': current_stats['diversity_ratio'],
            'by_type': current_stats['by_type'],
            'avg_reward': current_stats['avg_reward']
        }

        metrics['iterations'].append(iteration_metrics)

        print(f"\nIteration {i+1}/{num_iterations} Summary:")
        print(f"  Success rate: {success_rate:.1%} ({num_added}/{candidates_per_iteration})")
        print(f"  Total examples: {current_stats['total_examples']}")
        print(f"  Unique slow queries: {current_stats['unique_slow_queries']} ({current_stats['diversity_ratio']:.1%} diversity)")
        print(f"  Avg reward: {current_stats['avg_reward']:.2f}")
        print(f"  Time: {iteration_time:.1f}s")

        # Save checkpoint every 10 iterations
        if (i + 1) % 10 == 0:
            checkpoint_path = f"{output_dir}/checkpoint_iter_{i+1}.json"
            optimizer.save_training_data(checkpoint_path)
            print(f"  Checkpoint saved: {checkpoint_path}")

    total_time = time.time() - start_time

    metrics['end_time'] = datetime.now().isoformat()
    metrics['total_time_seconds'] = total_time
    metrics['final_stats'] = optimizer.get_stats()
    metrics['summary'] = {
        'total_candidates': total_candidates,
        'total_successful': total_generated,
        'overall_success_rate': total_generated / total_candidates if total_candidates > 0 else 0,
        'examples_gained': metrics['final_stats']['total_examples'] - metrics['initial_stats']['total_examples'],
        'unique_slow_queries': metrics['final_stats']['unique_slow_queries'],
        'diversity_ratio': metrics['final_stats']['diversity_ratio']
    }

    # Save final results
    final_data_path = f"{output_dir}/training_data.json"
    optimizer.save_training_data(final_data_path)

    metrics_path = f"{output_dir}/metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Stage 2 Training Complete!")
    print(f"{'='*70}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Total candidates: {total_candidates}")
    print(f"Successful: {total_generated} ({metrics['summary']['overall_success_rate']:.1%})")
    print(f"Final dataset size: {metrics['final_stats']['total_examples']}")
    print(f"Unique slow queries: {metrics['final_stats']['unique_slow_queries']}")
    print(f"Diversity: {metrics['final_stats']['diversity_ratio']:.1%}")
    print(f"\nBy optimization type:")
    for opt_type, count in metrics['final_stats']['by_type'].items():
        print(f"  {opt_type}: {count}")
    print(f"\nAverage reward: {metrics['final_stats']['avg_reward']:.2f}")
    print(f"\nData saved to: {final_data_path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"{'='*70}\n")

    return optimizer, metrics


if __name__ == "__main__":
    optimizer, metrics = run_stage2_training(
        num_iterations=100,
        candidates_per_iteration=5,
        reward_threshold=0.5,
        num_runs=3,
        timeout_seconds=10
    )
