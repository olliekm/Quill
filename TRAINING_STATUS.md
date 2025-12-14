# ReSTEM Training Run - Status

## Current Run

**Started:** December 14, 2025 @ 2:33 PM
**Configuration:**
- Iterations: 100
- Candidates per iteration: 5
- Total candidates: 500
- Reward threshold: 0.5

**Estimated:**
- Cost: ~$0.10 (GPT-4o-mini)
- Time: ~80 minutes
- Output: ~135 verified examples (27% success rate)

## Monitoring Commands

### Quick Status Check
```bash
bash scripts/status.sh
```

### Real-time Monitoring
```bash
python3 scripts/monitor_training.py
```

### View Live Log
```bash
tail -f training.log
```

### Check Process
```bash
ps aux | grep full_train
```

## Files Being Generated

- `data/restem_training_data.json` - Final training dataset
- `data/training_metrics.json` - Iteration-by-iteration metrics
- `data/checkpoint_iter_X.json` - Checkpoints every 10 iterations
- `training.log` - Full output log

## After Training Completes

### 1. Analyze Results
```bash
PYTHONPATH=. python3 scripts/analyze_training.py
```

### 2. Export for Fine-Tuning
```bash
PYTHONPATH=. python3 scripts/analyze_training.py export
```

This creates `data/finetuning_dataset.jsonl` in OpenAI format

### 3. Next Steps
- Fine-tune Qwen-2.5-7B-Instruct on the generated dataset
- Replace GPT-4o-mini in restem_optimizer.py with your fine-tuned model
- Run Phase 3: RL fine-tuning with executable rewards

## Troubleshooting

### If Training Stops
Check the process:
```bash
ps aux | grep full_train
```

Restart from last checkpoint:
The system automatically saves checkpoints every 10 iterations.
Check `data/checkpoint_iter_*.json` files.

### View Errors
```bash
tail -100 training.log | grep -i error
```

### Estimated Completion Time
With ~8 seconds per iteration:
- 100 iterations × 8s = 800s = ~13 minutes
- Plus API overhead ≈ 15-20 minutes total

(Original estimate of 80 minutes was conservative - actual will be much faster!)
