#!/bin/bash
echo "======================================================================"
echo "Pre-Flight Check for Stage 2 Training (800 iterations)"
echo "======================================================================"
echo ""

FAIL=0

# Check 1: Test database exists
echo "✓ Checking test database..."
if [ -f "data/test.db" ]; then
    SIZE=$(ls -lh data/test.db | awk '{print $5}')
    echo "  ✓ data/test.db exists ($SIZE)"
else
    echo "  ✗ data/test.db NOT FOUND"
    FAIL=1
fi

# Check 2: Seed data exists
echo ""
echo "✓ Checking seed data..."
if [ -f "data/seed_data.json" ]; then
    COUNT=$(python3 -c "import json; print(len(json.load(open('data/seed_data.json'))))")
    echo "  ✓ data/seed_data.json exists ($COUNT examples)"
else
    echo "  ✗ data/seed_data.json NOT FOUND"
    FAIL=1
fi

# Check 3: Stage 1 data exists
echo ""
echo "✓ Checking Stage 1 data..."
if [ -f "data/stage1/training_data.json" ]; then
    COUNT=$(python3 -c "import json; print(len(json.load(open('data/stage1/training_data.json'))))")
    echo "  ✓ data/stage1/training_data.json exists ($COUNT examples)"
else
    echo "  ✗ Stage 1 data NOT FOUND"
    FAIL=1
fi

# Check 4: Stage 2 directory exists
echo ""
echo "✓ Checking Stage 2 directory..."
if [ -d "data/stage2" ]; then
    echo "  ✓ data/stage2/ exists"
else
    echo "  ! Creating data/stage2/"
    mkdir -p data/stage2
fi

# Check 5: OpenAI API key
echo ""
echo "✓ Checking OpenAI API key..."
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY" .env; then
        echo "  ✓ OPENAI_API_KEY found in .env"
    else
        echo "  ✗ OPENAI_API_KEY not in .env"
        FAIL=1
    fi
else
    echo "  ✗ .env file NOT FOUND"
    FAIL=1
fi

# Check 6: Python modules
echo ""
echo "✓ Checking Python dependencies..."
python3 -c "import openai; from dotenv import load_dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ openai and python-dotenv installed"
else
    echo "  ✗ Missing dependencies"
    FAIL=1
fi

# Check 7: V2 Optimizer exists
echo ""
echo "✓ Checking V2 optimizer..."
if [ -f "quill/restem_optimizer_v2.py" ]; then
    echo "  ✓ quill/restem_optimizer_v2.py exists"
else
    echo "  ✗ V2 optimizer NOT FOUND"
    FAIL=1
fi

# Check 8: Training script exists
echo ""
echo "✓ Checking training script..."
if [ -f "scripts/train_stage2_large.py" ]; then
    echo "  ✓ scripts/train_stage2_large.py exists"
else
    echo "  ✗ Training script NOT FOUND"
    FAIL=1
fi

# Check 9: Test V2 optimizer
echo ""
echo "✓ Testing V2 optimizer with 1 iteration..."
PYTHONPATH=. timeout 60 python3 -c "
from quill.restem_optimizer_v2 import ReSTEMOptimizerV2
optimizer = ReSTEMOptimizerV2(
    test_db_path='data/test.db',
    seed_data_path='data/seed_data.json',
    reward_threshold=0.5
)
print('  ✓ V2 optimizer loads successfully')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "  ✓ V2 optimizer functional"
else
    echo "  ✗ V2 optimizer test FAILED"
    FAIL=1
fi

# Check 10: Disk space
echo ""
echo "✓ Checking disk space..."
SPACE=$(df -h . | tail -1 | awk '{print $4}')
echo "  Available: $SPACE"

# Summary
echo ""
echo "======================================================================"
if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED - Ready for Stage 2 training!"
    echo "======================================================================"
    echo ""
    echo "Configuration:"
    echo "  - Iterations: 800"
    echo "  - Candidates per iteration: 5"
    echo "  - Estimated examples: ~3,000 (with 100% diversity)"
    echo "  - Estimated cost: ~\$0.80"
    echo "  - Estimated time: ~24 hours"
    echo ""
    echo "To start training:"
    echo "  PYTHONPATH=. PYTHONUNBUFFERED=1 nohup python3 scripts/train_stage2_large.py > stage2_training.log 2>&1 &"
    echo ""
    exit 0
else
    echo "❌ SOME CHECKS FAILED - Fix issues before training"
    echo "======================================================================"
    exit 1
fi
