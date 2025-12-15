# ⚡ Quill Fine-Tuning - Quick Start

## 🎯 What You Need

- RunPod account (runpod.io)
- $5 balance (training costs ~$1.70)
- These 3 files uploaded:
  1. `quill_training_data.jsonl` (11 MB)
  2. `setup.sh`
  3. `finetune_quill.py`

---

## 📋 Complete Checklist

### Before SSH

- [ ] Deploy RTX 4090 pod on RunPod
- [ ] Copy SSH command and password
- [ ] Upload 3 files via scp

### After SSH

- [ ] Run `bash setup.sh` (2 min)
- [ ] Verify files: `ls -lh`
- [ ] Start training: `python3 finetune_quill.py`
- [ ] Wait ~5 hours
- [ ] Download model via scp
- [ ] Stop pod on RunPod dashboard

---

## 🚀 Super Quick Version

```bash
# 1. Deploy pod on runpod.io (RTX 4090, PyTorch template)

# 2. Upload files (from Mac)
scp -P <port> data/finetuning/quill_training_data.jsonl root@<host>:/workspace/
scp -P <port> runpod/*.{sh,py} root@<host>:/workspace/

# 3. SSH in
ssh root@<host> -p <port>

# 4. Setup + Train
bash setup.sh
python3 finetune_quill.py  # 5 hours

# 5. Download (from Mac)
scp -P <port> -r root@<host>:/workspace/quill-qwen-7b ./

# 6. Stop pod (runpod.io dashboard)
```

---

## 💰 Cost: ~$1.70 for complete training

---

## 📞 Need Help?

Check `RUNPOD_INSTRUCTIONS.md` for detailed step-by-step guide.
