#!/bin/bash

echo "========================================================================"
echo "Quill Fine-Tuning Setup for RunPod"
echo "========================================================================"

# Check CUDA
echo ""
echo "Checking GPU..."
nvidia-smi

# Check PyTorch
echo ""
echo "Checking PyTorch..."
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

# Install dependencies
echo ""
echo "Installing fine-tuning dependencies..."
pip install --quiet transformers==4.44.0 \
            datasets==2.19.0 \
            peft==0.11.0 \
            bitsandbytes==0.43.1 \
            trl==0.9.0 \
            accelerate==0.31.0 \
            sentencepiece \
            protobuf

echo ""
echo "========================================================================"
echo "✅ Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "  1. Verify training data: ls -lh quill_training_data.jsonl"
echo "  2. Run training: python3 finetune_quill.py"
echo "  3. Monitor with: watch -n 1 nvidia-smi"
echo ""
echo "========================================================================"
