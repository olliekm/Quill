#!/bin/bash
echo "======================================================================"
echo "Pre-Flight Check for Stage 2 Training (800 iterations)"
echo "======================================================================"
echo ""

FAIL=0

# Check 1: Test database exists
echo "1. Checking test database..."
if [ -f "data/test.db" ]; then
    SIZE=$(ls -lh data/test.db | awk '{print $5}')
    echo "   ✓ data/test.db exists ($SIZE)"
else
    echo "   ✗ data/test.db NOT FOUND"
    FAIL=1
fi

# Check 2: Seed data exists
echo "2. Checking seed data..."
if [ -f "data/seed_data.json" ]; then
    COUNT=$(python3 -c "import json; print(len(json.load(open('data/seed_data.json'))))" 2>/dev/null)
    echo "   ✓ data/seed_data.json exists ($COUNT examples)"
else
    echo "   ✗ data/seed_data.json NOT FOUND"
    FAIL=1
fi

# Check 3: Stage 1 data exists
echo "3. Checking Stage 1 data..."
if [ -f "data/stage1/training_data.json" ]; then
    COUNT=$(python3 -c "import json; print(len(json.load(open('data/stage1/training_data.json'))))" 2>/dev/null)
    echo "   ✓ Stage 1 complete ($COUNT examples)"
else
    echo "   ✗ Stage 1 data NOT FOUND"
    FAIL=1
fi

# Check 4: OpenAI API key
echo "4. Checking OpenAI API key..."
if [ -f ".env" ] && grep -q "OPENAI_API_KEY" .env; then
    echo "   ✓ OPENAI_API_KEY configured"
else
    echo "   ✗ OPENAI_API_KEY not found"
    FAIL=1
fi

# Check 5: Python modules
echo "5. Checking Python dependencies..."
python3 -c "import openai; from dotenv import load_dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ All dependencies installed"
else
    echo "   ✗ Missing dependencies (run: pip install -r requirements.txt)"
    FAIL=1
fi

# Check 6: V2 Optimizer
echo "6. Checking V2 optimizer..."
if [ -f "quill/restem_optimizer_v2.py" ]; then
    echo "   ✓ V2 optimizer ready"
else
    echo "   ✗ V2 optimizer NOT FOUND"
    FAIL=1
fi

# Check 7: Directories
echo "7. Checking directories..."
mkdir -p data/stage2
echo "   ✓ data/stage2/ ready"

# Check 8: Disk space
echo "8. Checking disk space..."
SPACE=$(df -h . | tail -1 | awk '{print $4}')
echo "   ✓ Available: $SPACE"

# Summary
echo ""
echo "======================================================================"
if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED"
    echo "======================================================================"
    echo ""
    echo "📊 Configuration:"
    echo "   Iterations: 800"
    echo "   Candidates per iteration: 5"
    echo "   Total candidates: 4,000"
    echo "   Expected success rate: ~75%"
    echo "   Expected examples: ~3,000 (100% diversity)"
    echo ""
    echo "💰 Cost Estimate:"
    echo "   ~\$0.80 (GPT-4o-mini)"
    echo ""
    echo "⏱️  Time Estimate:"
    echo "   ~24 hours (can run overnight)"
    echo ""
    echo "🚀 To start training:"
    echo "   PYTHONPATH=. PYTHONUNBUFFERED=1 nohup python3 scripts/train_stage2_large.py > stage2_training.log 2>&1 &"
    echo ""
    echo "📈 Monitor progress:"
    echo "   tail -f stage2_training.log"
    echo "   python3 scripts/monitor_training.py"
    echo ""
    exit 0
else
    echo "❌ CHECKS FAILED - Fix issues first"
    echo "======================================================================"
    exit 1
fi
