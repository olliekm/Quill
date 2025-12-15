# 🚀 RunPod Fine-Tuning Instructions for Quill

## Step 1: Deploy RunPod Pod

1. Go to **[runpod.io](https://runpod.io)** and create account
2. Click **"Deploy"** → **"GPU Pods"**
3. **Select GPU:** RTX 4090 (24GB) - $0.34/hour
4. **Choose Template:** `RunPod PyTorch 2.1.0`
   - Or search: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel`
5. **Configure Storage:**
   - Container Disk: 50 GB
   - Volume: 50 GB (persistent)
6. **Deploy Pod** (takes ~2 minutes to start)

---

## Step 2: Get SSH Connection Info

Once deployed, RunPod will show:

```
SSH Access:
ssh root@abc123-456def-789.runpod.io -p 12345
Password: XyZ9AbC123
```

**Copy these details!**

---

## Step 3: Upload Files to RunPod

From your Mac terminal (in the Quill directory):

```bash
# Set your pod details (replace with your actual values)
POD_HOST="abc123-456def-789.runpod.io"
POD_PORT="12345"

# Upload all files
scp -P $POD_PORT data/finetuning/quill_training_data.jsonl root@$POD_HOST:/workspace/
scp -P $POD_PORT runpod/setup.sh root@$POD_HOST:/workspace/
scp -P $POD_PORT runpod/finetune_quill.py root@$POD_HOST:/workspace/

# Enter password when prompted (3 times)
```

**Alternative - Upload one by one:**
```bash
scp -P 12345 data/finetuning/quill_training_data.jsonl root@abc123.runpod.io:/workspace/
scp -P 12345 runpod/setup.sh root@abc123.runpod.io:/workspace/
scp -P 12345 runpod/finetune_quill.py root@abc123.runpod.io:/workspace/
```

---

## Step 4: Connect via SSH

```bash
# Connect to your pod
ssh root@abc123-456def-789.runpod.io -p 12345

# Enter password when prompted
```

---

## Step 5: Setup Environment

Once connected via SSH, run:

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
bash setup.sh
```

This will:
- Check GPU status
- Verify PyTorch installation
- Install fine-tuning dependencies (~2 minutes)

---

## Step 6: Verify Files

```bash
# Check all files are present
ls -lh

# You should see:
# - quill_training_data.jsonl (11 MB)
# - setup.sh
# - finetune_quill.py
```

---

## Step 7: Start Training

### Option A: Run Directly (Simple)
```bash
python3 finetune_quill.py
```

### Option B: Run in tmux (Recommended)
```bash
# Start tmux session
tmux new -s training

# Run training
python3 finetune_quill.py

# Detach: Press Ctrl+B, then D
# Reattach later: tmux attach -t training
```

**Training will take ~4-6 hours**

---

## Step 8: Monitor Training

### In a new terminal (from your Mac):
```bash
# Connect again
ssh root@abc123.runpod.io -p 12345

# Watch GPU usage
watch -n 1 nvidia-smi

# Or check process
ps aux | grep finetune
```

### Inside tmux (if using):
```bash
# Reattach to see progress
tmux attach -t training
```

---

## Step 9: Download Trained Model

After training completes (~4-6 hours):

```bash
# From your Mac terminal
scp -P 12345 -r root@abc123.runpod.io:/workspace/quill-qwen-7b ./

# This downloads the LoRA adapters (~100 MB)
```

---

## Step 10: Stop Pod (Save Money!)

**Important:** RunPod charges per minute!

1. Go to RunPod dashboard
2. Click **"Stop"** or **"Terminate"** on your pod
3. Verify it's stopped (no more charges)

**Cost breakdown:**
- Setup: ~5 minutes = $0.03
- Training: ~5 hours = $1.70
- **Total: ~$1.73**

---

## Troubleshooting

### "Permission denied" when uploading
- Check you're using the correct port: `-P 12345`
- Verify password is correct

### "Connection refused"
- Pod might still be starting (wait 2 minutes)
- Check pod status in RunPod dashboard

### "CUDA out of memory"
- This shouldn't happen with our config
- If it does, in `finetune_quill.py` change:
  ```python
  per_device_train_batch_size=1  # Was 2
  gradient_accumulation_steps=16  # Was 8
  ```

### "Module not found"
- Re-run: `bash setup.sh`
- Or install manually: `pip install transformers datasets peft trl`

### Training seems stuck
- It's normal for first steps to be slow (model loading)
- Check GPU usage: `nvidia-smi`
- Should see ~22GB VRAM used

---

## Expected Output

During training, you'll see:

```
Epoch 1/3: 100%|██████████| 963/963 [1:45:23<00:00,  6.54s/it]
Eval Loss: 0.523
Saving checkpoint...

Epoch 2/3: 100%|██████████| 963/963 [1:44:12<00:00,  6.49s/it]
Eval Loss: 0.312
Saving checkpoint...

Epoch 3/3: 100%|██████████| 963/963 [1:43:54<00:00,  6.47s/it]
Eval Loss: 0.287
Training complete!
```

---

## Files You'll Get

After training:

```
quill-qwen-7b/
├── adapter_config.json          # LoRA configuration
├── adapter_model.safetensors   # LoRA weights (~100 MB)
├── tokenizer_config.json
├── tokenizer.json
└── special_tokens_map.json
```

These are the **LoRA adapters** - you load them on top of the base Qwen model.

---

## Cost Summary

| Item | Time | Cost |
|------|------|------|
| Setup | 5 min | $0.03 |
| Training (3 epochs) | 5 hours | $1.70 |
| **Total** | **~5 hours** | **~$1.73** |

**Much cheaper than training on your laptop's electricity!**

---

## Next Steps After Training

See `TRAINING_COMPLETE.md` for:
- How to load and use the fine-tuned model
- Evaluation strategies
- Inference examples
- Deployment options

---

## Quick Reference

```bash
# Upload files
scp -P <port> quill_training_data.jsonl root@<host>:/workspace/

# Connect
ssh root@<host> -p <port>

# Setup
bash setup.sh

# Train (with tmux)
tmux new -s training
python3 finetune_quill.py

# Detach: Ctrl+B, D
# Reattach: tmux attach -t training

# Download model
scp -P <port> -r root@<host>:/workspace/quill-qwen-7b ./

# Stop pod (save money!)
# Go to runpod.io dashboard → Stop
```

---

**Ready? Let's go! 🚀**
