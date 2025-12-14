# Quill - SQL Query Optimizer via ReSTEM

Self-improving SQL query optimizer using ReSTEM (Reward-optimized Self-Training for Executable Models).

## Architecture

### Phase 1: Data Generation (Current)
Generate large training dataset using ReSTEM loop:
1. Sample seed examples for few-shot prompting
2. Generate optimization candidates with LLM (GPT-4o-mini)
3. Execute and evaluate on real SQLite database
4. Filter by reward threshold (correctness + speedup)
5. Add successful examples back to training set
6. Repeat with improved few-shot examples

### Phase 2: Supervised Fine-Tuning (Next)
Fine-tune Qwen on generated dataset:
- Input: schema + slow_query
- Output: fast_query + explanation

### Phase 3: RL Fine-Tuning (Future)
Use ReSTEM rewards to RL-train Qwen via PPO/DPO

## Project Structure

```
quill/
├── evaluator.py          # SQL performance evaluator (correctness + speedup)
├── llm_judge.py          # LLM-as-Judge for readability scoring
├── restem_optimizer.py   # ReSTEM self-improving loop
scripts/
├── seed_collector.py     # Generate test database (10k users, 50k orders)
├── train_restem.py       # Multi-iteration training with metrics
├── analyze_training.py   # Analyze metrics and export for fine-tuning
examples/
├── test_evaluation.py    # Test evaluator on seed data
├── test_llm_judge.py     # Test readability judge
data/
├── seed_data.json        # 20 hand-crafted seed examples
├── test.db               # SQLite test database (gitignored)
└── restem_training_data.json  # Generated training data (gitignored)
```

## Quick Start

### 1. Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY
```

### 2. Generate Test Database
```bash
PYTHONPATH=. python3 scripts/seed_collector.py
```

### 3. Test Evaluator
```bash
PYTHONPATH=. python3 examples/test_evaluation.py
```

### 4. Run Single ReSTEM Iteration
```bash
PYTHONPATH=. python3 quill/restem_optimizer.py
```

### 5. Run Multi-Iteration Training (Generate Dataset)
```bash
PYTHONPATH=. python3 scripts/train_restem.py
```

This will:
- Run 50 iterations
- Generate 5 candidates per iteration
- Track metrics (success rate, rewards, diversity)
- Save checkpoints every 10 iterations
- Output: `data/restem_training_data.json` (100+ examples)

### 6. Analyze Training Results
```bash
PYTHONPATH=. python3 scripts/analyze_training.py
```

### 7. Export for Fine-Tuning
```bash
PYTHONPATH=. python3 scripts/analyze_training.py export
```

Output: `data/finetuning_dataset.jsonl` in OpenAI fine-tuning format

## Reward Function

```
reward = speedup_reward + readability_bonus

speedup_reward = min(1.0, log(speedup + 1) / log(10))
  - 1x speedup → 0.3 reward
  - 10x speedup → 1.0 reward
  - 100x speedup → 1.0 reward (capped)

readability_bonus = [-0.2, +0.2]
  - LLM judges which query is more readable
  - Bonus if optimized is more readable
  - Penalty if optimized is less readable
```

## Optimization Types

- **indexing**: Add indexes (CREATE INDEX)
- **join**: Replace subqueries with JOINs
- **projection**: SELECT specific columns instead of *
- **limit**: Add LIMIT for top-N queries
- **redundancy**: Remove duplicate computations

## Configuration

Edit `scripts/train_restem.py` to customize:
- `num_iterations`: Number of ReSTEM loops (default: 50)
- `candidates_per_iteration`: Candidates per loop (default: 5)
- `reward_threshold`: Minimum reward to accept (default: 0.5)
- `timeout_seconds`: Query timeout (default: 10s)

## Metrics Tracked

- Success rate per iteration
- Distribution by optimization type
- Average reward over time
- Total examples generated
- Checkpoints for recovery

## Next Steps

1. ✅ Phase 1: Generate 100+ training examples
2. ⏳ Phase 2: Fine-tune Qwen on generated data
3. ⏳ Phase 3: RL fine-tune with ReSTEM rewards
4. ⏳ Build API/CLI for inference
