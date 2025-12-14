# Quill Training Strategy - Research Notes

## Core Research Question
**Can we train a small LLM (7B params) to optimize SQL queries using self-improvement with executable feedback?**

---

## Training Data Distribution Design

### Reward Function (Real-World Aligned)

```
Speedup    Reward    Frequency in Production
1.5x   →   0.25      Common (SELECT *, missing single index)
2x     →   0.45      Very Common (basic indexing)
5x     →   0.60      Common (composite indexes, IN vs OR)
10x    →   0.70      Moderate (JOIN instead of subquery)
50x    →   0.85      Rare (correlated subquery on medium data)
1000x+ →   0.95      Very Rare (pathological cases, large datasets)
```

**Reward Threshold: 0.25** (accept 1.5x+ speedups)

**Rationale:**
- Most production SQL optimizations yield 2-20x speedups
- Training should reflect real-world distribution
- Model needs to learn that even 2x speedup is worth doing
- Extreme speedups (1000x+) are edge cases, shouldn't dominate dataset

---

## Known Limitations & Distribution Shift

### Current Setup
- **Database:** 10K users, 50K orders (single table)
- **Scale:** Unrealistically large for SQLite
- **Speedups:** Biased toward 1000x+ from correlated subqueries

### Real-World Production
- **Small apps:** 100-10K rows per table
- **Medium apps:** 10K-1M rows, multiple tables
- **Large apps:** Sharded/distributed (not single SQLite)
- **Speedups:** Mostly 2-50x from missing indexes

### Mitigation Strategy
1. **Reward function:** Emphasize 2-50x speedups over 1000x+
2. **Threshold:** Accept realistic optimizations (1.5x+)
3. **Future work:** Add more realistic schemas (small-medium tables)

---

## Stage 2 Training Goals

### Target Dataset Characteristics
- **Size:** 1,000-1,500 examples (quality over quantity)
- **Diversity:** 100% unique slow queries
- **Distribution:**
  - 50% modest speedups (2-10x): indexing, projection
  - 30% good speedups (10-100x): JOIN optimization
  - 20% exceptional speedups (100x+): avoid pathological patterns

### Success Metrics
- ✅ High diversity (avoid memorization)
- ✅ Balanced speedup distribution
- ✅ Executable correctness (100% correct results)
- ✅ Realistic query patterns (junior dev mistakes, not artificial)

---

## What We're Learning

### Optimization Patterns (Priority Order)
1. **Indexing** (most common)
   - Single-column indexes on WHERE filters
   - Composite indexes for multi-column filters
   - JOIN indexes (foreign keys)

2. **Query Structure** (common)
   - Subquery → JOIN conversion
   - OR chains → IN clauses
   - SELECT * → specific columns

3. **Avoid Pathological** (rare but critical)
   - Correlated subqueries
   - Cartesian products
   - Missing WHERE clauses

---

## Training Process (ReSTEM)

### Self-Improvement Loop
```
1. Sample schema from seed data
2. LLM generates "junior dev" slow query
3. LLM generates optimization
4. Execute both queries on real database
5. Verify correctness (results must match)
6. Calculate reward (speedup + readability)
7. If reward ≥ 0.25: add to training set
8. New examples become few-shot examples for next iteration
```

### Why This Works
- **Executable feedback:** Ground truth from real database
- **Self-improvement:** Training set grows with verified examples
- **Curriculum:** Learns from own successful optimizations
- **Diversity:** New queries each iteration (100% diversity)

---

## Next Steps (After Stage 2)

### 1. Schema Augmentation (4x multiplier)
- Rename tables (users → customers, employees, members)
- Rename columns (age → customer_age, employee_age)
- Preserves optimization patterns, increases diversity

### 2. Fine-Tuning (Qwen 2.5 7B)
- **Method:** LoRA/QLoRA (parameter-efficient)
- **Format:** Instruction tuning (schema + slow query → optimized query)
- **Dataset:** ~4,000-6,000 examples after augmentation

### 3. RL Fine-Tuning (Optional)
- **DPO:** Learn preferences between optimizations
- **PPO:** Optimize for speedup reward directly
- **Goal:** Further improve beyond supervised examples

---

## Research Validity Checks

### ✅ Strengths
- Real executable feedback (not LLM judge)
- High diversity (unique queries)
- Self-improving (ReSTEM)
- Correctness guaranteed (results verification)

### ⚠️ Limitations Acknowledged
- **Distribution shift:** Training on larger dataset than typical production
- **Schema diversity:** Currently only 2 tables (users, orders)
- **Optimization types:** Biased toward JOIN/indexing patterns

### 🎯 Mitigations Applied
- Reward function emphasizes realistic speedups
- Lower threshold accepts common optimizations
- Junior dev prompt generates realistic mistakes
- Future: Add more schemas, tables, patterns

---

## Expected Outcomes

### After Fine-Tuning
The model should learn to:
1. Identify missing indexes (WHERE, JOIN columns)
2. Recognize when to use JOINs vs subqueries
3. Simplify query structure (OR → IN, SELECT *)
4. Avoid pathological patterns (correlated subqueries)

### Evaluation Metrics
1. **Correctness:** Does optimized query return same results?
2. **Speedup:** Average speedup on held-out test set
3. **Diversity:** Can it handle different schemas/patterns?
4. **Practical:** Would a dev actually use this optimization?

---

## Cost Analysis

### Stage 2 Training (800 iterations)
- **API calls:** ~8,000 GPT-4o-mini calls
- **Cost:** ~$0.80 (0.1¢ per example)
- **Time:** ~24 hours
- **Output:** ~1,500 verified examples

### Fine-Tuning (Qwen 2.5 7B)
- **Method:** QLoRA on single GPU
- **Dataset:** ~6,000 examples (post-augmentation)
- **Time:** 4-8 hours on RTX 4090
- **Cost:** Compute only (no API calls)

**Total project cost: < $5** (mostly API calls)

---

## Conclusion

This training strategy balances:
- **Research rigor:** Executable feedback, verified correctness
- **Practical value:** Real-world speedup distribution
- **Efficiency:** Low cost, high-quality data
- **Diversity:** 100% unique queries, avoid overfitting

The key insight: **Train on realistic optimizations (2-50x) that developers encounter daily, not just pathological edge cases (1000x+).**
