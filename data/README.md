# Data Organization

## Directory Structure

```
data/
├── seed_data.json           # 20 hand-crafted seed examples
├── test.db                  # SQLite test database (10k users, 50k orders)
├── stage1/                  # Low diversity, high volume (technique learning)
│   ├── training_data.json   # 467 examples, 20 unique slow queries
│   ├── metrics.json         # Training metrics
│   └── checkpoint_*.json    # Checkpoints every 10 iterations
├── stage2/                  # High diversity (generalization)
│   ├── training_data.json   # Generated with unique slow queries
│   ├── metrics.json         # Training metrics
│   └── checkpoint_*.json    # Checkpoints
└── combined/                # Stage 1 + Stage 2 combined for fine-tuning
    └── training_data.json   # Final dataset for Qwen

finetuning_datasets/         # Export formats for different platforms
├── openai_format.jsonl      # OpenAI fine-tuning format
├── huggingface_format.json  # HuggingFace datasets format
└── qwen_format.jsonl        # Qwen-specific format
```

## Stage Descriptions

### Stage 1: Technique Learning ✅ COMPLETE
**Purpose:** Learn optimization techniques and patterns

**Characteristics:**
- 467 total examples (20 seed + 447 generated)
- 20 unique slow queries (reused from seed)
- 60 unique fast queries (different optimization approaches)
- 4.3% slow query diversity
- 89.4% success rate
- 0.96 average reward

**Value:**
- Multiple ways to optimize the same query
- Learn indexing, JOIN, projection techniques
- High success rate → high-quality examples
- Cost: ~$0.10

**Limitation:**
- Low diversity → overfitting risk
- Only learns to optimize 20 query patterns

---

### Stage 2: Generalization 🔄 IN PROGRESS
**Purpose:** High diversity for generalization

**Characteristics:**
- Generates NEW slow queries each iteration
- High slow query diversity (target: >80%)
- Same schemas as Stage 1
- Cost: ~$0.10-0.20

**Value:**
- Teaches model to generalize
- Prevents overfitting to specific queries
- Broader pattern coverage

**Method:**
- Uses `restem_optimizer_v2.py`
- LLM generates new slow queries
- Optimizes them
- Evaluates on real DB

---

### Combined: Final Training Dataset
**Purpose:** Best of both worlds

**Contents:**
- Stage 1: 467 examples (technique depth)
- Stage 2: ~400 examples (pattern diversity)
- Total: ~850-900 examples

**Fine-tuning Strategy:**
```python
# Curriculum learning approach
1. Train on Stage 1 (learn techniques)
2. Continue training on Stage 2 (generalize)
3. Or: Weighted sampling (30% Stage 1, 70% Stage 2)
```

---

## Stage Comparison

| Metric | Stage 1 | Stage 2 (Target) |
|--------|---------|------------------|
| Total Examples | 467 | ~400 |
| Unique Slow Queries | 20 | ~400 |
| Diversity | 4.3% | ~100% |
| Success Rate | 89.4% | ~70-80% |
| Purpose | Technique Learning | Generalization |
| Model | GPT-4o-mini | GPT-4o-mini |
| Cost | $0.10 | $0.10-0.20 |

---

## How to Use

### Generate Stage 2 Data
```bash
PYTHONPATH=. python3 scripts/train_stage2.py
```

### Combine Datasets
```bash
PYTHONPATH=. python3 scripts/combine_stages.py
```

### Export for Fine-Tuning
```bash
# OpenAI format
PYTHONPATH=. python3 scripts/export_finetuning.py --stage combined --format openai

# HuggingFace format
PYTHONPATH=. python3 scripts/export_finetuning.py --stage combined --format huggingface
```

---

## Key Insights

**Stage 1 Discovery:**
- ReSTEM self-improvement works! (66% → 96% success rate)
- BUT: Low diversity limits generalization
- 467 examples of optimizing 20 queries = overfitting risk

**Stage 2 Solution:**
- Generate new slow queries each iteration
- Higher diversity = better generalization
- Combined with Stage 1 = depth + breadth

**Fine-Tuning Recommendation:**
Use curriculum learning:
1. Start with Stage 1 (learn optimization techniques)
2. Continue with Stage 2 (learn to generalize)
3. Test on held-out schemas to validate
