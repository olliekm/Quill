"""
Estimate OpenAI API costs for ReSTEM training
"""

# GPT-4o-mini pricing (as of late 2024)
INPUT_COST_PER_1M = 0.150  # $0.15 per 1M input tokens
OUTPUT_COST_PER_1M = 0.600  # $0.60 per 1M output tokens

def estimate_training_cost(
    num_iterations=50,
    candidates_per_iteration=5,
    avg_input_tokens_per_candidate=800,  # Schema + slow query + 3 few-shot examples
    avg_output_tokens_per_candidate=150  # Optimized query + explanation
):
    """
    Estimate total cost for ReSTEM training run
    """

    total_candidates = num_iterations * candidates_per_iteration

    # Generation costs
    total_input_tokens = total_candidates * avg_input_tokens_per_candidate
    total_output_tokens = total_candidates * avg_output_tokens_per_candidate

    input_cost = (total_input_tokens / 1_000_000) * INPUT_COST_PER_1M
    output_cost = (total_output_tokens / 1_000_000) * OUTPUT_COST_PER_1M
    generation_cost = input_cost + output_cost

    print(f"{'='*70}")
    print(f"OpenAI API Cost Estimate - GPT-4o-mini")
    print(f"{'='*70}\n")

    print(f"Configuration:")
    print(f"  Iterations: {num_iterations}")
    print(f"  Candidates per iteration: {candidates_per_iteration}")
    print(f"  Total candidates: {total_candidates}\n")

    print(f"Token Estimates (per candidate):")
    print(f"  Input tokens: ~{avg_input_tokens_per_candidate:,}")
    print(f"  Output tokens: ~{avg_output_tokens_per_candidate:,}\n")

    print(f"Total Tokens:")
    print(f"  Input: {total_input_tokens:,} tokens")
    print(f"  Output: {total_output_tokens:,} tokens\n")

    print(f"Cost Breakdown:")
    print(f"  Input cost:  ${input_cost:.4f} ({total_input_tokens:,} tokens @ ${INPUT_COST_PER_1M}/1M)")
    print(f"  Output cost: ${output_cost:.4f} ({total_output_tokens:,} tokens @ ${OUTPUT_COST_PER_1M}/1M)")
    print(f"  {'─'*70}")
    print(f"  Total cost:  ${generation_cost:.4f}\n")

    # Success rate estimate
    success_rate = 0.27  # Based on test run
    successful_examples = int(total_candidates * success_rate)
    cost_per_successful_example = generation_cost / successful_examples if successful_examples > 0 else 0

    print(f"Expected Results (based on {success_rate:.0%} success rate):")
    print(f"  Successful examples: ~{successful_examples}")
    print(f"  Cost per successful example: ${cost_per_successful_example:.4f}\n")

    print(f"{'='*70}")
    print(f"ESTIMATED TOTAL COST: ${generation_cost:.2f}")
    print(f"{'='*70}\n")

    # Different scenarios
    print(f"Cost Scenarios:")
    print(f"  10 iterations:  ${generation_cost * 0.2:.2f}")
    print(f"  25 iterations:  ${generation_cost * 0.5:.2f}")
    print(f"  50 iterations:  ${generation_cost:.2f}")
    print(f"  100 iterations: ${generation_cost * 2:.2f}\n")

    return generation_cost


if __name__ == "__main__":
    estimate_training_cost()
