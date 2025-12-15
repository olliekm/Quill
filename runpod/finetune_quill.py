"""
Fine-tune Qwen 2.5 7B on Quill SQL optimization dataset
Using QLoRA for memory-efficient training
"""

import os
import json
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

print("=" * 70)
print("Quill Fine-Tuning - Qwen 2.5 7B with QLoRA")
print("=" * 70)

# Configuration
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
DATA_PATH = "quill_training_data.jsonl"
OUTPUT_DIR = "./quill-qwen-7b"

# Check if data exists
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Training data not found: {DATA_PATH}")

print(f"\n✓ Model: {MODEL_NAME}")
print(f"✓ Data: {DATA_PATH}")
print(f"✓ Output: {OUTPUT_DIR}")

# Load dataset
print("\n" + "=" * 70)
print("Loading Dataset")
print("=" * 70)

dataset = load_dataset('json', data_files=DATA_PATH)
print(f"✓ Loaded {len(dataset['train'])} examples")

# Split train/validation (90/10)
dataset = dataset['train'].train_test_split(test_size=0.1, seed=42)
print(f"✓ Train: {len(dataset['train'])} examples")
print(f"✓ Val: {len(dataset['test'])} examples")

# QLoRA configuration for 4-bit quantization
print("\n" + "=" * 70)
print("Configuring 4-bit Quantization (QLoRA)")
print("=" * 70)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

print("✓ 4-bit quantization enabled")
print("✓ Compute dtype: float16")
print("✓ Double quantization: True")

# Load model
print("\n" + "=" * 70)
print("Loading Qwen 2.5 7B...")
print("=" * 70)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.float16,
)

print("✓ Model loaded in 4-bit mode")

# Prepare model for k-bit training
model = prepare_model_for_kbit_training(model)
print("✓ Model prepared for QLoRA training")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    padding_side="right",
)

# Set pad token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id

print("✓ Tokenizer loaded")

# LoRA configuration
print("\n" + "=" * 70)
print("Configuring LoRA Adapters")
print("=" * 70)

lora_config = LoraConfig(
    r=16,                          # LoRA rank
    lora_alpha=32,                 # LoRA alpha
    target_modules=[               # Qwen attention layers
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
print("✓ LoRA adapters configured")

# Print trainable parameters
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
all_params = sum(p.numel() for p in model.parameters())
print(f"✓ Trainable params: {trainable_params:,} / {all_params:,} ({100 * trainable_params / all_params:.2f}%)")

# Format dataset for chat
print("\n" + "=" * 70)
print("Formatting Dataset")
print("=" * 70)

def format_chat_template(example):
    """Format messages into Qwen chat template"""
    messages = example['messages']

    # Convert to chat format
    formatted = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )

    return {"text": formatted}

# Apply formatting
dataset = dataset.map(format_chat_template, remove_columns=dataset['train'].column_names)
print("✓ Dataset formatted for Qwen chat template")

# Training arguments
print("\n" + "=" * 70)
print("Training Configuration")
print("=" * 70)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,           # Effective batch size: 2 * 8 = 16
    gradient_checkpointing=True,
    optim="paged_adamw_32bit",
    learning_rate=2e-4,
    weight_decay=0.01,
    fp16=True,
    max_grad_norm=0.3,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    save_strategy="epoch",
    save_total_limit=2,
    load_best_model_at_end=True,
    report_to="none",                        # No wandb/tensorboard
    seed=42,
)

print(f"✓ Epochs: {training_args.num_train_epochs}")
print(f"✓ Batch size: {training_args.per_device_train_batch_size}")
print(f"✓ Gradient accumulation: {training_args.gradient_accumulation_steps}")
print(f"✓ Effective batch size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
print(f"✓ Learning rate: {training_args.learning_rate}")
print(f"✓ Warmup ratio: {training_args.warmup_ratio}")
print(f"✓ Optimizer: {training_args.optim}")

# Initialize trainer
print("\n" + "=" * 70)
print("Initializing Trainer")
print("=" * 70)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset['train'],
    eval_dataset=dataset['test'],
    peft_config=lora_config,
    dataset_text_field="text",
    max_seq_length=2048,
    tokenizer=tokenizer,
    args=training_args,
)

print("✓ Trainer initialized")

# Start training
print("\n" + "=" * 70)
print("Starting Training")
print("=" * 70)
print("\nThis will take approximately 4-6 hours on RTX 4090...")
print("You can monitor GPU usage with: watch -n 1 nvidia-smi")
print("\n" + "=" * 70 + "\n")

trainer.train()

# Save final model
print("\n" + "=" * 70)
print("Saving Model")
print("=" * 70)

trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"✓ Model saved to: {OUTPUT_DIR}")

# Print training summary
print("\n" + "=" * 70)
print("Training Complete!")
print("=" * 70)
print(f"\nModel saved to: {OUTPUT_DIR}")
print(f"\nTo use the model:")
print(f"  1. Download: scp -r root@<pod>:/workspace/{OUTPUT_DIR} ./")
print(f"  2. Load in Python:")
print(f"     from peft import PeftModel")
print(f"     base = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-7B-Instruct')")
print(f"     model = PeftModel.from_pretrained(base, '{OUTPUT_DIR}')")
print("\n" + "=" * 70)
