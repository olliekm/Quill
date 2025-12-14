# Stage 2 Training - Monitoring Guide

## Training Started
- **PID:** 8003
- **Log file:** `stage2_training.log`
- **Started:** December 14, 2025
- **Expected completion:** ~24 hours
- **Expected output:** ~3,000 examples (100% diversity)

---

## Quick Monitoring Commands

### Check if still running
```bash
ps aux | grep train_stage2_large | grep -v grep
# Or check PID file:
cat stage2_training.pid
ps -p $(cat stage2_training.pid)
```

### Live log tail (press Ctrl+C to exit, won't stop training)
```bash
tail -f stage2_training.log
```

### See latest progress
```bash
tail -50 stage2_training.log
```

### Check iteration count
```bash
grep "Iteration.*Summary" stage2_training.log | tail -5
```

### Check diversity stats
```bash
grep "Unique slow queries" stage2_training.log | tail -1
```

### Check latest checkpoint
```bash
ls -lht data/stage2/checkpoint_*.json | head -1
```

### Monitor with status script (updates every 10s)
```bash
# Note: This will read from data/stage2/metrics.json
# First checkpoint saves at iteration 10
python3 scripts/monitor_training.py
```

---

## Progress Checkpoints

Training saves checkpoints every 10 iterations:
- `data/stage2/checkpoint_iter_10.json`
- `data/stage2/checkpoint_iter_20.json`
- ... up to 800

---

## Expected Milestones

| Iterations | Expected Examples | Diversity | ETA |
|------------|------------------|-----------|-----|
| 100 | ~375 | 95%+ | ~3 hours |
| 200 | ~750 | 97%+ | ~6 hours |
| 400 | ~1,500 | 98%+ | ~12 hours |
| 800 | ~3,000 | 99%+ | ~24 hours |

---

## If You Need to Stop

```bash
# Get PID
cat stage2_training.pid

# Stop gracefully
kill $(cat stage2_training.pid)

# Force stop (if needed)
kill -9 $(cat stage2_training.pid)
```

Note: Latest checkpoint will be saved in `data/stage2/`

---

## After Completion

When training finishes, you'll see in the log:
```
Stage 2 complete! Next steps:
```

Then run:

### 1. Analyze results
```bash
PYTHONPATH=. python3 -c "
import json
with open('data/stage2/training_data.json') as f:
    data = json.load(f)
unique = len(set(ex['slow_query'].strip() for ex in data))
print(f'Total: {len(data)} examples')
print(f'Unique slow queries: {unique}')
print(f'Diversity: {unique/len(data):.1%}')
"
```

### 2. Run schema augmentation (4x multiplier)
```bash
PYTHONPATH=. python3 scripts/augment_schemas.py
```

### 3. Export for fine-tuning
```bash
PYTHONPATH=. python3 scripts/analyze_training.py export
```

---

## Current Status Commands

Run these anytime to check progress:

```bash
# Quick status
tail -20 stage2_training.log | grep -E "Iteration|Success rate|Diversity"

# Full recent output
tail -100 stage2_training.log
```
