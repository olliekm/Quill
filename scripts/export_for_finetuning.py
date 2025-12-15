"""
Export dataset for Qwen fine-tuning in chat format
"""

import json
from typing import List, Dict

def format_for_qwen(examples: List[Dict]) -> List[Dict]:
    """
    Convert examples to Qwen chat format

    Format:
    {
        "messages": [
            {"role": "system", "content": "You are a SQL query optimizer..."},
            {"role": "user", "content": "Schema:\n...\n\nSlow Query:\n..."},
            {"role": "assistant", "content": "Optimized Query:\n..."}
        ]
    }
    """

    system_prompt = """You are Quill, an expert SQL query optimizer. Given a database schema and a slow SQL query, you generate an optimized version that:
1. Returns identical results (correctness guaranteed)
2. Runs significantly faster
3. Uses proper indexing strategies
4. Follows SQL best practices

Your optimizations may include:
- Adding appropriate indexes (single-column, composite)
- Converting correlated subqueries to JOINs
- Removing SELECT * in favor of specific columns
- Using WHERE clause efficiently
- Optimizing GROUP BY and aggregations
- Eliminating redundant operations"""

    formatted = []

    for ex in examples:
        schema = ex.get('schema', '').strip()
        slow_query = ex.get('slow_query', '').strip()
        fast_query = ex.get('fast_query', '').strip()
        explanation = ex.get('explanation', '').strip()

        if not schema or not slow_query or not fast_query:
            continue

        user_message = f"""Schema:
{schema}

Slow Query:
{slow_query}

Please provide an optimized version of this query."""

        assistant_message = f"""Optimized Query:
{fast_query}

Explanation: {explanation}"""

        formatted.append({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message}
            ]
        })

    return formatted


def export_dataset(input_path: str, output_path: str, format: str = "qwen"):
    """Export dataset in specified format"""

    print("=" * 70)
    print(f"Exporting Dataset for Fine-Tuning")
    print("=" * 70)

    # Load data
    print(f"\nLoading from: {input_path}")
    with open(input_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded: {len(data)} examples")

    # Format data
    print(f"\nFormatting for: {format}")

    if format == "qwen":
        formatted = format_for_qwen(data)
    else:
        raise ValueError(f"Unknown format: {format}")

    print(f"Formatted: {len(formatted)} examples")

    # Save
    print(f"\nSaving to: {output_path}")
    with open(output_path, 'w') as f:
        for item in formatted:
            f.write(json.dumps(item) + '\n')

    print(f"\n✅ Export complete!")
    print(f"  Input: {len(data)} examples")
    print(f"  Output: {len(formatted)} examples")
    print(f"  Format: {format} (JSONL)")
    print(f"  File: {output_path}")

    # Print sample
    print(f"\n📋 Sample Entry:")
    print("=" * 70)
    sample = formatted[0]
    for msg in sample['messages']:
        print(f"\n[{msg['role'].upper()}]")
        content = msg['content']
        if len(content) > 300:
            content = content[:300] + "..."
        print(content)

    print("\n" + "=" * 70)
    print("Ready for Qwen Fine-Tuning!")
    print("=" * 70)

    return formatted


if __name__ == "__main__":
    import sys
    import os

    # Default paths
    input_path = "data/combined/training_data_augmented.json"
    output_dir = "data/finetuning"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Export for Qwen
    output_path = os.path.join(output_dir, "quill_training_data.jsonl")
    export_dataset(input_path, output_path, format="qwen")

    print(f"\n🚀 Next Steps:")
    print(f"  1. Upload {output_path} to your training environment")
    print(f"  2. Use with Qwen 2.5 7B Instruct")
    print(f"  3. Fine-tune with LoRA/QLoRA")
    print(f"  4. Evaluate on held-out test set")
