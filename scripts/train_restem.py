"""
Multi-iteration ReSTEM training loop with metrics tracking
Runs multiple iterations to build a large, high-quality training dataset
"""

import sys
sys.path.insert(0, '..')

import json
import time
from datetime import datetime
from quill.restem_optimizer import ReSTEMOptimizer


def run_training(
    num_iterations=50,
    candidates_per_iteration=5,
    reward_threshold=0.5,
    num_runs=3,
    timeout_seconds=10,
    output_dir="data"
):
    """
    Run multi-iteration ReSTEM training

    Args:
        num_iterations: Number of ReSTEM iterations to run
        candidates_per_iteration: Candidates to generate per iteration
        reward_threshold: Minimum reward to accept a candidate
        num_runs: Number of timing runs for evaluation
        timeout_seconds: Query timeout limit
        output_dir: Where to save results
    """

    print(f"\n{'='*70}")
    print(f"ReSTEM Multi-Iteration Training")
    print(f"{'='*70}")
    print(f"Iterations: {num_iterations}")
    print(f"Candidates per iteration: {candidates_per_iteration}")
    print(f"Reward threshold: {reward_threshold}")
    print(f"{'='*70}\n")

    optimizer = ReSTEMOptimizer(
        test_db_path=f"{output_dir}/test.db",
        seed_data_path=f"{output_dir}/seed_data.json",
        reward_threshold=reward_threshold
    )

    metrics = {
        'start_time': datetime.now().isoformat(),
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
            'by_type': current_stats['by_type'],
            'avg_reward': current_stats['avg_reward']
        }

        metrics['iterations'].append(iteration_metrics)

        print(f"\nIteration {i+1}/{num_iterations} Summary:")
        print(f"  Success rate: {success_rate:.1%} ({num_added}/{candidates_per_iteration})")
        print(f"  Total examples: {current_stats['total_examples']}")
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
        'examples_gained': metrics['final_stats']['total_examples'] - metrics['initial_stats']['total_examples']
    }

    # Save final results
    final_data_path = f"{output_dir}/restem_training_data.json"
    optimizer.save_training_data(final_data_path)

    metrics_path = f"{output_dir}/training_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Training Complete!")
    print(f"{'='*70}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Total candidates: {total_candidates}")
    print(f"Successful: {total_generated} ({metrics['summary']['overall_success_rate']:.1%})")
    print(f"Final dataset size: {metrics['final_stats']['total_examples']}")
    print(f"Examples gained: {metrics['summary']['examples_gained']}")
    print(f"\nBy optimization type:")
    for opt_type, count in metrics['final_stats']['by_type'].items():
        print(f"  {opt_type}: {count}")
    print(f"\nAverage reward: {metrics['final_stats']['avg_reward']:.2f}")
    print(f"\nData saved to: {final_data_path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"{'='*70}\n")

    return optimizer, metrics


if __name__ == "__main__":
    optimizer, metrics = run_training(
        num_iterations=50,
        candidates_per_iteration=5,
        reward_threshold=0.5,
        num_runs=3,
        timeout_seconds=10
    )
