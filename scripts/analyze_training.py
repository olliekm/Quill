"""
Analyze ReSTEM training metrics and display progress
"""

import json
import sys


def analyze_metrics(metrics_path="data/training_metrics.json"):
    """Analyze and display training metrics"""

    with open(metrics_path, 'r') as f:
        metrics = json.load(f)

    print(f"\n{'='*70}")
    print(f"ReSTEM Training Analysis")
    print(f"{'='*70}\n")

    print(f"Training Period: {metrics['start_time']} to {metrics['end_time']}")
    print(f"Total Duration: {metrics['total_time_seconds']/60:.1f} minutes")
    print(f"Configuration: {metrics['config']['num_iterations']} iterations, "
          f"{metrics['config']['candidates_per_iteration']} candidates/iter\n")

    print(f"{'='*70}")
    print(f"Overall Results")
    print(f"{'='*70}")
    print(f"Initial examples: {metrics['initial_stats']['total_examples']}")
    print(f"Final examples: {metrics['final_stats']['total_examples']}")
    print(f"Examples gained: {metrics['summary']['examples_gained']}")
    print(f"Total candidates: {metrics['summary']['total_candidates']}")
    print(f"Successful: {metrics['summary']['total_successful']}")
    print(f"Success rate: {metrics['summary']['overall_success_rate']:.1%}")
    print(f"Avg reward: {metrics['final_stats']['avg_reward']:.2f}\n")

    print(f"{'='*70}")
    print(f"Distribution by Optimization Type")
    print(f"{'='*70}")
    for opt_type, count in sorted(metrics['final_stats']['by_type'].items(),
                                   key=lambda x: x[1], reverse=True):
        pct = count / metrics['final_stats']['total_examples'] * 100
        print(f"{opt_type:15s}: {count:4d} ({pct:5.1f}%)")

    # Analyze success rate over time
    if len(metrics['iterations']) > 0:
        print(f"\n{'='*70}")
        print(f"Success Rate by Iteration Window")
        print(f"{'='*70}")

        window_size = 10
        for i in range(0, len(metrics['iterations']), window_size):
            window = metrics['iterations'][i:i+window_size]
            total_candidates = sum(it['candidates_generated'] for it in window)
            total_successful = sum(it['successful'] for it in window)
            success_rate = total_successful / total_candidates if total_candidates > 0 else 0
            avg_reward = sum(it['avg_reward'] for it in window) / len(window)

            print(f"Iterations {i+1:2d}-{min(i+window_size, len(metrics['iterations'])):2d}: "
                  f"{success_rate:5.1%} success, {avg_reward:.2f} avg reward, "
                  f"{total_successful} new examples")

        # Best and worst iterations
        print(f"\n{'='*70}")
        print(f"Best Iterations")
        print(f"{'='*70}")
        sorted_iters = sorted(metrics['iterations'],
                             key=lambda x: x['successful'],
                             reverse=True)[:5]

        for it in sorted_iters:
            print(f"Iteration {it['iteration']:2d}: {it['successful']} successful "
                  f"({it['success_rate']:.0%}), avg reward {it['avg_reward']:.2f}")

    print(f"\n{'='*70}\n")


def export_for_finetuning(
    training_data_path="data/restem_training_data.json",
    output_path="data/finetuning_dataset.jsonl"
):
    """
    Export training data in format for fine-tuning

    Format: {"messages": [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]}
    """

    with open(training_data_path, 'r') as f:
        training_data = json.load(f)

    with open(output_path, 'w') as f:
        for example in training_data:
            user_content = f"""Optimize this SQL query for performance.

Schema:
{example['schema']}

Query to optimize:
{example['slow_query']}"""

            assistant_content = f"""{example['fast_query']}

Explanation: {example['explanation']}
Optimization type: {example['optimization_type']}"""

            message = {
                "messages": [
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content}
                ]
            }

            f.write(json.dumps(message) + '\n')

    print(f"Exported {len(training_data)} examples to {output_path}")
    print(f"Ready for fine-tuning with OpenAI or other platforms")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_for_finetuning()
    else:
        analyze_metrics()
