"""
Monitor ongoing ReSTEM training progress
"""

import json
import os
import time
from datetime import datetime

def monitor_training(metrics_path="data/training_metrics.json", refresh_seconds=10):
    """Monitor training progress by reading metrics file"""

    print("Monitoring ReSTEM training...")
    print("Press Ctrl+C to stop monitoring (training continues)\n")

    last_iteration = 0

    try:
        while True:
            if not os.path.exists(metrics_path):
                print(f"Waiting for training to start... ({datetime.now().strftime('%H:%M:%S')})")
                time.sleep(refresh_seconds)
                continue

            try:
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)

                current_iteration = len(metrics.get('iterations', []))

                if current_iteration > last_iteration:
                    last_iteration = current_iteration
                    config = metrics['config']
                    total_iters = config['num_iterations']

                    # Get latest iteration stats
                    if current_iteration > 0:
                        latest = metrics['iterations'][-1]

                        # Calculate overall progress
                        total_candidates = sum(it['candidates_generated'] for it in metrics['iterations'])
                        total_successful = sum(it['successful'] for it in metrics['iterations'])
                        overall_success_rate = total_successful / total_candidates if total_candidates > 0 else 0

                        # Time estimate
                        elapsed = time.time() - time.mktime(time.strptime(metrics['start_time'][:19], '%Y-%m-%dT%H:%M:%S'))
                        avg_time_per_iter = elapsed / current_iteration
                        remaining_iters = total_iters - current_iteration
                        eta_seconds = avg_time_per_iter * remaining_iters
                        eta_minutes = eta_seconds / 60

                        print(f"\n{'='*70}")
                        print(f"Iteration {current_iteration}/{total_iters} ({current_iteration/total_iters*100:.1f}%)")
                        print(f"{'='*70}")
                        print(f"Latest iteration:")
                        print(f"  Success: {latest['successful']}/{latest['candidates_generated']} ({latest['success_rate']:.1%})")
                        print(f"  Avg reward: {latest['avg_reward']:.2f}")
                        print(f"  Time: {latest['time_seconds']:.1f}s")
                        print(f"\nOverall progress:")
                        print(f"  Total examples: {latest['total_examples']}")
                        print(f"  Generated: {total_successful} ({overall_success_rate:.1%} success rate)")
                        print(f"  Elapsed: {elapsed/60:.1f} min")
                        print(f"  ETA: {eta_minutes:.1f} min")
                        print(f"{'='*70}")

                        # Show distribution
                        if 'by_type' in latest:
                            print(f"Distribution: ", end="")
                            print(", ".join([f"{k}: {v}" for k, v in sorted(latest['by_type'].items(), key=lambda x: x[1], reverse=True)]))

                time.sleep(refresh_seconds)

            except json.JSONDecodeError:
                # File being written, try again
                time.sleep(1)
                continue

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped. Training continues in background.")
        print("Check training.log for full output")
        print("Re-run this script to resume monitoring")


if __name__ == "__main__":
    import sys
    refresh = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    monitor_training(refresh_seconds=refresh)
