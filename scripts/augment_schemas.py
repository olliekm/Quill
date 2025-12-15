"""
Schema Augmentation - 4x Data Multiplication
Generates variations with different table/column names
"""

import json
import re
from typing import Dict, List

# Schema name mappings (4 variations per table)
SCHEMA_VARIANTS = {
    # E-commerce
    'users': ['customers', 'accounts', 'members'],
    'orders': ['purchases', 'transactions', 'sales'],
    # Social network
    'posts': ['articles', 'messages', 'updates'],
    'comments': ['replies', 'responses', 'feedback'],
    # HR system
    'employees': ['staff', 'workers', 'personnel'],
    # Analytics
    'events': ['activities', 'actions', 'logs'],
    # Content platform
    'articles': ['documents', 'content', 'publications'],
    'tags': ['categories', 'labels', 'topics'],
    'article_tags': ['document_categories', 'content_labels', 'publication_topics']
}

COLUMN_VARIANTS = {
    'users': {
        'age': ['customer_age', 'account_age', 'member_age'],
        'city': ['location', 'area', 'region'],
        'email': ['contact_email', 'user_email', 'member_email'],
        'name': ['full_name', 'display_name', 'username'],
        'signup_date': ['registration_date', 'join_date', 'created_date']
    },
    'orders': {
        'user_id': ['customer_id', 'buyer_id', 'account_id'],
        'amount': ['total', 'price', 'cost'],
        'product': ['item', 'sku', 'product_name'],
        'order_date': ['purchase_date', 'transaction_date', 'sale_date']
    },
    'posts': {
        'user_id': ['author_id', 'creator_id', 'poster_id'],
        'title': ['subject', 'heading', 'topic'],
        'content': ['body', 'text', 'message'],
        'likes': ['reactions', 'votes', 'favorites'],
        'created_at': ['posted_at', 'published_at', 'timestamp']
    },
    'comments': {
        'post_id': ['article_id', 'message_id', 'update_id'],
        'user_id': ['author_id', 'commenter_id', 'responder_id'],
        'text': ['content', 'body', 'message'],
        'created_at': ['posted_at', 'timestamp', 'comment_date']
    },
    'employees': {
        'manager_id': ['supervisor_id', 'boss_id', 'lead_id'],
        'department': ['division', 'team', 'unit'],
        'salary': ['compensation', 'pay', 'wage'],
        'hire_date': ['start_date', 'join_date', 'employment_date']
    },
    'events': {
        'user_id': ['account_id', 'visitor_id', 'session_user_id'],
        'event_type': ['action_type', 'activity_type', 'event_name'],
        'properties': ['metadata', 'attributes', 'data'],
        'timestamp': ['event_time', 'occurred_at', 'created_at']
    },
    'articles': {
        'author_id': ['writer_id', 'creator_id', 'publisher_id'],
        'title': ['heading', 'subject', 'name'],
        'content': ['body', 'text', 'description'],
        'views': ['reads', 'visits', 'impressions'],
        'published_at': ['created_at', 'posted_at', 'release_date']
    },
    'tags': {
        'name': ['label', 'category', 'topic']
    }
}


def apply_schema_mapping(text: str, table_mapping: Dict[str, str], column_mapping: Dict[str, str]) -> str:
    """Apply table and column name mappings to SQL text"""

    # Replace table names (case-insensitive, word boundaries)
    for old_table, new_table in table_mapping.items():
        # Match table names in various contexts
        patterns = [
            (rf'\bFROM\s+{old_table}\b', f'FROM {new_table}'),
            (rf'\bJOIN\s+{old_table}\b', f'JOIN {new_table}'),
            (rf'\b{old_table}\s+\w+\s+ON\b', lambda m: m.group(0).replace(old_table, new_table)),
            (rf'\bON\s+{old_table}(\.\w+)', f'ON {new_table}\\1'),
            (rf'\b{old_table}\.', f'{new_table}.'),
            (rf'\bCREATE\s+TABLE\s+{old_table}\b', f'CREATE TABLE {new_table}'),
            (rf'\bINTO\s+{old_table}\b', f'INTO {new_table}'),
            (rf'idx_{old_table}_', f'idx_{new_table}_'),  # Fix index names
        ]

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Replace column names
    for old_col, new_col in column_mapping.items():
        # Match column names in various contexts
        patterns = [
            (rf'\b{old_col}\b(?!\s*\()', new_col),  # Not followed by ( to avoid function names
            (rf'\({old_col}\)', f'({new_col})'),
            (rf'idx_\w*_{old_col}', lambda m: m.group(0).replace(old_col, new_col)),
        ]

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.MULTILINE)

    return text


def generate_variants(example: Dict, variant_index: int) -> Dict:
    """Generate a schema variant for an example"""

    # Build table mapping
    table_mapping = {}
    for table, variants in SCHEMA_VARIANTS.items():
        if variant_index < len(variants):
            table_mapping[table] = variants[variant_index]
        else:
            table_mapping[table] = table

    # Build column mapping
    column_mapping = {}
    for table, columns in COLUMN_VARIANTS.items():
        for old_col, variants in columns.items():
            if variant_index < len(variants):
                column_mapping[old_col] = variants[variant_index]
            else:
                column_mapping[old_col] = old_col

    # Apply mappings
    variant = {
        'id': example.get('id', 0) * 10 + variant_index + 1,  # Unique ID
        'description': f"{example.get('description', 'Augmented')} (variant {variant_index + 1})",
        'schema': apply_schema_mapping(example['schema'], table_mapping, column_mapping),
        'slow_query': apply_schema_mapping(example['slow_query'], table_mapping, column_mapping),
        'fast_query': apply_schema_mapping(example['fast_query'], table_mapping, column_mapping),
        'explanation': example['explanation'],
        'optimization_type': example['optimization_type']
    }

    return variant


def augment_dataset(input_path: str, output_path: str, num_variants: int = 3):
    """
    Augment dataset with schema variants

    Args:
        input_path: Path to original dataset
        output_path: Path to save augmented dataset
        num_variants: Number of variants per example (default 3, creates 4x data)
    """

    print(f"Loading dataset from {input_path}...")
    with open(input_path, 'r') as f:
        data = json.load(f)

    print(f"Original dataset: {len(data)} examples")

    augmented = []

    # Add original examples
    augmented.extend(data)

    # Generate variants
    for variant_idx in range(num_variants):
        print(f"Generating variant {variant_idx + 1}/{num_variants}...")
        for example in data:
            try:
                variant = generate_variants(example, variant_idx)
                augmented.append(variant)
            except Exception as e:
                print(f"  Warning: Failed to generate variant for example {example.get('id')}: {e}")

    print(f"Augmented dataset: {len(augmented)} examples ({len(augmented)/len(data):.1f}x)")

    # Save
    print(f"Saving to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(augmented, f, indent=2)

    print(f"✓ Augmentation complete!")
    print(f"  Original: {len(data)} examples")
    print(f"  Augmented: {len(augmented)} examples")
    print(f"  Multiplier: {len(augmented)/len(data):.1f}x")


def augment_combined_dataset():
    """Augment combined Stage 1 + Stage 2 dataset"""

    print("="*70)
    print("Schema Augmentation - Combined Dataset")
    print("="*70 + "\n")

    # First combine Stage 1 and Stage 2
    print("Step 1: Combining Stage 1 and Stage 2...")

    stage1_path = "data/stage1/training_data.json"
    stage2_path = "data/stage2/training_data.json"
    combined_path = "data/combined/training_data_original.json"
    augmented_path = "data/combined/training_data_augmented.json"

    # Load both stages
    with open(stage1_path, 'r') as f:
        stage1 = json.load(f)

    try:
        with open(stage2_path, 'r') as f:
            stage2 = json.load(f)
    except FileNotFoundError:
        print("Warning: Stage 2 data not found. Using only Stage 1.")
        stage2 = []

    # Combine
    combined = stage1 + stage2
    print(f"  Stage 1: {len(stage1)} examples")
    print(f"  Stage 2: {len(stage2)} examples")
    print(f"  Combined: {len(combined)} examples\n")

    # Save original combined
    with open(combined_path, 'w') as f:
        json.dump(combined, f, indent=2)
    print(f"  Saved to {combined_path}\n")

    # Augment
    print("Step 2: Generating schema variants...")
    augment_dataset(combined_path, augmented_path, num_variants=3)

    print(f"\n{'='*70}")
    print(f"Augmentation Complete!")
    print(f"{'='*70}")
    print(f"Final dataset: {augmented_path}")
    print(f"Ready for fine-tuning!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Augment specific file
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_augmented.json')
        augment_dataset(input_file, output_file)
    else:
        # Augment combined dataset
        augment_combined_dataset()
