#!/bin/bash
# Quick training status check

echo "==================================================================="
echo "ReSTEM Training Status"
echo "==================================================================="
echo ""

# Check if process is running
if ps aux | grep -v grep | grep "full_train.py" > /dev/null; then
    echo "✓ Training is RUNNING"
    PID=$(ps aux | grep -v grep | grep "full_train.py" | awk '{print $2}')
    echo "  Process ID: $PID"
    echo ""
else
    echo "✗ Training is NOT running"
    echo ""
    exit 1
fi

# Check metrics file
if [ -f "data/training_metrics.json" ]; then
    echo "Progress:"
    python3 -c "
import json
with open('data/training_metrics.json') as f:
    m = json.load(f)
    iters = len(m.get('iterations', []))
    total = m['config']['num_iterations']
    if iters > 0:
        latest = m['iterations'][-1]
        total_successful = sum(it['successful'] for it in m['iterations'])
        print(f\"  Iterations: {iters}/{total} ({iters/total*100:.1f}%)\")
        print(f\"  Total examples: {latest['total_examples']}\")
        print(f\"  Successful generated: {total_successful}\")
        print(f\"  Latest success rate: {latest['success_rate']:.1%}\")
    else:
        print(f\"  Initializing... (0/{total} iterations)\")
"
else
    echo "  Metrics file not created yet (still initializing)"
fi

echo ""
echo "==================================================================="
echo "To monitor in real-time: python3 scripts/monitor_training.py"
echo "To view log: tail -f training.log"
echo "==================================================================="
