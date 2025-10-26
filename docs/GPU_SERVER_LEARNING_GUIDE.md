# GPU Server Learning Guide: Hands-On AI/ML Experiments

## 🎯 What You Can Learn with a $0.09/hr GPU Server

Since you're keeping API keys local (smart!), here are **practical experiments** you can run on a cheap GPU server to learn about inference, model testing, and optimization.

**Cost:** $0.09-0.19/hr on Vast.ai or RunPod
**Time:** 10-20 hours of learning
**Total Investment:** $1-4 to learn enterprise-level AI skills

---

## 📚 Learning Path Overview

| Experiment | What You'll Learn | Time | Value |
|------------|------------------|------|-------|
| **1. Multi-Model Comparison** | Compare 5-10 different LLMs | 2-3 hrs | ⭐⭐⭐⭐⭐ |
| **2. Quantization Testing** | Test 4-bit, 8-bit, 16-bit models | 1-2 hrs | ⭐⭐⭐⭐ |
| **3. Prompt Engineering** | Optimize prompts for accuracy | 2-3 hrs | ⭐⭐⭐⭐⭐ |
| **4. Fine-Tuning Workshop** | Actually fine-tune Llama 3.2 | 3-5 hrs | ⭐⭐⭐⭐⭐ |
| **5. Performance Benchmarking** | Measure tokens/sec, latency | 1-2 hrs | ⭐⭐⭐⭐ |
| **6. RAG System Building** | Build document Q&A system | 2-4 hrs | ⭐⭐⭐⭐⭐ |
| **7. Model Serving Setup** | Deploy as API endpoint | 2-3 hrs | ⭐⭐⭐⭐ |
| **8. Multi-GPU Training** | Learn distributed computing | 3-4 hrs | ⭐⭐⭐ |

**Total:** ~20 hours of hands-on learning for $2-4

---

## 🚀 Experiment 1: Multi-Model Comparison (HIGHLY RECOMMENDED)

### What You'll Learn:
- How different models perform on same task
- Model size vs accuracy tradeoffs
- Speed vs quality comparisons
- Which models work best for your use case

### Models to Test:

```bash
# Install Ollama on GPU server
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# Pull various models (different sizes/capabilities)
ollama pull llama3.2:1b        # 1B params - tiny, fast
ollama pull llama3.2:3b        # 3B params - what you tested
ollama pull llama3.1:8b        # 8B params - balanced
ollama pull mistral:7b         # Mistral - strong competitor
ollama pull phi3:3.8b          # Microsoft's model
ollama pull gemma2:9b          # Google's model
ollama pull qwen2.5:7b         # Alibaba's model
ollama pull deepseek-r1:7b     # DeepSeek reasoning model
```

### Test Script:

Create `multi_model_test.py`:

```python
"""
Multi-Model Comparison Test
Compare different LLMs on HR leave policy evaluation
"""

import requests
import json
import time
from datetime import datetime

# Models to test
MODELS = [
    "llama3.2:1b",
    "llama3.2:3b",
    "llama3.1:8b",
    "mistral:7b",
    "phi3:3.8b",
    "gemma2:9b",
    "qwen2.5:7b",
    "deepseek-r1:7b"
]

# Test case: The one Llama 3.2 3B failed
TEST_PROMPT = """You are an HR policy analyst.

Annual Leave Policy:
- Max Consecutive Days: 15
- Annual Quota: 21 days

Leave Request:
- Employee: Mike Johnson
- Duration: 8 days
- Current Balance: 21 days

Question: Is this request within policy? Answer with:
1. YES or NO
2. Your reasoning (one sentence)

Format: YES/NO | Reason
"""

def test_model(model_name):
    """Test a single model"""
    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": TEST_PROMPT,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_gpu": -1
                }
            },
            timeout=60
        )

        end_time = time.time()
        elapsed = end_time - start_time

        result = response.json()
        answer = result['response'].strip()

        # Check if answer starts with YES or NO
        is_correct = answer.upper().startswith("YES")

        print(f"Response: {answer[:200]}...")
        print(f"Time: {elapsed:.2f}s")
        print(f"Correct: {'✅' if is_correct else '❌'}")

        return {
            "model": model_name,
            "answer": answer,
            "time": elapsed,
            "correct": is_correct,
            "tokens_per_sec": result.get('eval_count', 0) / elapsed if elapsed > 0 else 0
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "model": model_name,
            "error": str(e),
            "correct": False
        }

def main():
    print("🔬 Multi-Model Comparison Test")
    print("Testing HR policy evaluation across 8 different models\n")

    results = []

    for model in MODELS:
        result = test_model(model)
        results.append(result)
        time.sleep(2)  # Cool down between tests

    # Summary report
    print(f"\n{'='*80}")
    print("SUMMARY REPORT")
    print(f"{'='*80}\n")

    print(f"{'Model':<25} {'Correct':<10} {'Time':<10} {'Tokens/sec':<12}")
    print("-" * 80)

    for r in results:
        if 'error' not in r:
            print(f"{r['model']:<25} "
                  f"{'✅' if r['correct'] else '❌':<10} "
                  f"{r['time']:.2f}s{'':<6} "
                  f"{r.get('tokens_per_sec', 0):.1f}")

    # Save results
    with open('model_comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✅ Results saved to model_comparison_results.json")

    # Winner
    correct_models = [r for r in results if r.get('correct', False)]
    if correct_models:
        fastest = min(correct_models, key=lambda x: x['time'])
        print(f"\n🏆 Best Model: {fastest['model']} ({fastest['time']:.2f}s)")

if __name__ == "__main__":
    main()
```

### What You'll Discover:
- Which models get the answer right (8 ≤ 15 = YES)
- Speed differences (1B vs 8B models)
- Quality vs performance tradeoffs
- Best model for your use case

**Expected Results:**
- Smaller models (1B, 3B): Faster but less accurate
- Larger models (7B, 8B, 9B): Slower but more accurate
- Some models excel at reasoning (DeepSeek, Qwen)

**Cost:** ~$0.30 for full test (30 min on $0.09/hr server)

---

## 🚀 Experiment 2: Quantization Comparison

### What You'll Learn:
- How quantization affects accuracy and speed
- 4-bit vs 8-bit vs 16-bit performance
- Memory usage tradeoffs

### Test Different Quantization Levels:

```bash
# Pull same model in different quantizations
ollama pull llama3.1:8b-instruct-q4_0     # 4-bit (smallest)
ollama pull llama3.1:8b-instruct-q5_1     # 5-bit (balanced)
ollama pull llama3.1:8b-instruct-q8_0     # 8-bit (larger, better)
ollama pull llama3.1:8b-instruct-fp16     # 16-bit (largest, best)
```

### Create `quantization_test.py`:

```python
"""
Test how quantization affects model performance
"""

import requests
import json
import time

QUANT_MODELS = [
    "llama3.1:8b-instruct-q4_0",   # ~4.7GB VRAM
    "llama3.1:8b-instruct-q5_1",   # ~5.5GB VRAM
    "llama3.1:8b-instruct-q8_0",   # ~8.5GB VRAM
    "llama3.1:8b-instruct-fp16",   # ~16GB VRAM
]

# Your HR test prompt here
TEST_PROMPT = "..." # Same as before

def test_quantization(model):
    """Test model with GPU monitoring"""
    print(f"\nTesting {model}")

    # Monitor VRAM before
    import subprocess
    vram_before = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]
    ).decode().strip()

    start = time.time()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": TEST_PROMPT, "stream": False}
    )
    elapsed = time.time() - start

    result = response.json()

    # Monitor VRAM after
    vram_after = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]
    ).decode().strip()

    return {
        "model": model,
        "time": elapsed,
        "vram_used": f"{vram_after}MB",
        "tokens_per_sec": result.get('eval_count', 0) / elapsed,
        "response": result['response'][:200]
    }

# Run tests and compare
for model in QUANT_MODELS:
    result = test_quantization(model)
    print(f"  Time: {result['time']:.2f}s")
    print(f"  VRAM: {result['vram_used']}")
    print(f"  Speed: {result['tokens_per_sec']:.1f} tok/s")
```

### What You'll Learn:
- 4-bit: 2x faster, uses 50% less VRAM, slightly less accurate
- 8-bit: Balanced - good speed and quality
- 16-bit: Best quality, slowest, needs most VRAM

**Cost:** ~$0.20 for testing (20 min)

---

## 🚀 Experiment 3: Fine-Tuning Workshop (MOST VALUABLE)

### What You'll Learn:
- How to fine-tune a model on custom data
- LoRA (Low-Rank Adaptation) technique
- Measuring improvement before/after
- Creating production-ready models

### Step-by-Step Fine-Tuning:

You already have the training data generator! Let's actually use it.

**Step 1: Generate Training Data**
```bash
# On GPU server
python3 generate_training_data.py
# Creates training_data.jsonl with 50 examples
```

**Step 2: Install Fine-Tuning Tools**
```bash
pip install unsloth transformers datasets peft trl torch
```

**Step 3: Fine-Tune Script**

Create `fine_tune_llama.py`:

```python
"""
Fine-tune Llama 3.2 on HR leave policy data
Using Unsloth for 2x faster training
"""

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,  # Use 4-bit for memory efficiency
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
)

# Load your training data
dataset = load_dataset("json", data_files="training_data.jsonl")

# Training configuration
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=100,  # Adjust based on dataset size
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        output_dir="./llama-hr-finetuned",
        optim="adamw_8bit",
    ),
)

# Start training!
print("🚀 Starting fine-tuning...")
trainer.train()

# Save fine-tuned model
model.save_pretrained("llama-hr-finetuned")
tokenizer.save_pretrained("llama-hr-finetuned")

print("✅ Fine-tuning complete!")
print("📁 Model saved to: llama-hr-finetuned/")
```

**Step 4: Test Before/After**

```python
# Test base model
base_accuracy = test_model("llama3.2:3b")  # ~67%

# Test fine-tuned model
finetuned_accuracy = test_model("llama-hr-finetuned")  # Expect 90-95%

print(f"Improvement: {finetuned_accuracy - base_accuracy:.1f}%")
```

### What You'll Learn:
- How fine-tuning actually works
- LoRA vs full fine-tuning
- How much data you need
- Accuracy improvements (67% → 90%+)
- How to save and deploy custom models

**Time:** 3-5 hours
**Cost:** ~$0.30-0.50 (GPU time)
**Value:** ⭐⭐⭐⭐⭐ (Enterprise skill)

---

## 🚀 Experiment 4: RAG System Building

### What You'll Learn:
- Retrieval-Augmented Generation (RAG)
- Vector embeddings and similarity search
- Building document Q&A systems
- Combining local LLMs with knowledge bases

### Build a RAG System:

```bash
pip install chromadb sentence-transformers
```

Create `rag_system.py`:

```python
"""
Build a RAG system for HR policy Q&A
"""

import chromadb
from sentence_transformers import SentenceTransformer
import requests

# 1. Load embedding model (runs on GPU)
print("Loading embedding model...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Create vector database
client = chromadb.Client()
collection = client.create_collection("hr_policies")

# 3. Load HR knowledge base
import json
with open('hr_knowledge_base.json') as f:
    kb = json.load(f)

# 4. Embed and store policies
print("Embedding HR policies...")
for policy_name, policy_data in kb['leave_policies'].items():
    text = f"{policy_data['name']}: {policy_data['description']}. "
    text += f"Annual quota: {policy_data['annual_quota']} days. "
    text += f"Max consecutive: {policy_data['max_consecutive_days']} days."

    embedding = embedder.encode(text).tolist()

    collection.add(
        ids=[policy_name],
        embeddings=[embedding],
        documents=[text],
        metadatas=[policy_data]
    )

# 5. Query function
def ask_hr_question(question):
    """Answer HR questions using RAG"""

    # Get relevant policies
    question_embedding = embedder.encode(question).tolist()
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    # Build context
    context = "Relevant HR Policies:\n"
    for doc in results['documents'][0]:
        context += f"- {doc}\n"

    # Ask LLM with context
    prompt = f"""{context}

Question: {question}

Answer based only on the policies above:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()['response']

# Test
print("\n🤖 RAG System Ready!\n")

questions = [
    "How many sick leave days do I get per year?",
    "What's the maximum consecutive days for annual leave?",
    "Do I need advance notice for casual leave?",
]

for q in questions:
    print(f"Q: {q}")
    answer = ask_hr_question(q)
    print(f"A: {answer}\n")
```

### What You'll Learn:
- How RAG works (retrieval + generation)
- Vector embeddings and semantic search
- Combining LLMs with knowledge bases
- Building production Q&A systems

**Time:** 2-4 hours
**Cost:** ~$0.20-0.40
**Value:** ⭐⭐⭐⭐⭐ (Very practical skill)

---

## 🚀 Experiment 5: Performance Benchmarking

### What You'll Learn:
- Measure tokens/second
- Latency vs throughput
- GPU utilization optimization
- Concurrent request handling

Create `benchmark.py`:

```python
"""
Comprehensive model performance benchmarking
"""

import requests
import time
import concurrent.futures
import numpy as np

def benchmark_model(model, prompt, num_runs=10):
    """Benchmark single model"""

    times = []
    tokens_per_sec = []

    for i in range(num_runs):
        start = time.time()

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_gpu": -1}
            }
        )

        elapsed = time.time() - start
        times.append(elapsed)

        result = response.json()
        tps = result.get('eval_count', 0) / elapsed
        tokens_per_sec.append(tps)

    return {
        "model": model,
        "avg_time": np.mean(times),
        "std_time": np.std(times),
        "avg_tokens_per_sec": np.mean(tokens_per_sec),
        "min_time": np.min(times),
        "max_time": np.max(times),
    }

def benchmark_concurrent(model, prompt, num_concurrent=5):
    """Test concurrent request handling"""

    start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [
            executor.submit(
                requests.post,
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            for _ in range(num_concurrent)
        ]

        results = [f.result() for f in futures]

    total_time = time.time() - start

    return {
        "concurrent_requests": num_concurrent,
        "total_time": total_time,
        "avg_time_per_request": total_time / num_concurrent,
        "throughput": num_concurrent / total_time
    }

# Run benchmarks
models = ["llama3.2:1b", "llama3.2:3b", "llama3.1:8b"]
prompt = "Explain machine learning in one sentence."

print("🔬 Performance Benchmark\n")

for model in models:
    print(f"\nBenchmarking {model}...")

    # Sequential benchmark
    seq_results = benchmark_model(model, prompt)
    print(f"  Avg Time: {seq_results['avg_time']:.2f}s ± {seq_results['std_time']:.2f}s")
    print(f"  Tokens/sec: {seq_results['avg_tokens_per_sec']:.1f}")

    # Concurrent benchmark
    conc_results = benchmark_concurrent(model, prompt, num_concurrent=3)
    print(f"  Concurrent (3 req): {conc_results['total_time']:.2f}s total")
    print(f"  Throughput: {conc_results['throughput']:.2f} req/sec")
```

### What You'll Learn:
- How to measure inference performance
- Concurrent vs sequential processing
- GPU batching effects
- Real-world throughput expectations

**Time:** 1-2 hours
**Cost:** ~$0.10-0.20

---

## 🚀 Experiment 6: Model Serving & API Setup

### What You'll Learn:
- Deploy model as REST API
- Load balancing across GPUs
- Production deployment patterns
- API authentication and rate limiting

### Setup Model Server:

```bash
pip install fastapi uvicorn
```

Create `model_server.py`:

```python
"""
Production-ready model serving API
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import requests
import time
from collections import deque
import threading

app = FastAPI(title="HR Policy AI API")

# Rate limiting
request_times = deque(maxlen=100)
RATE_LIMIT = 10  # requests per minute

class LeaveRequest(BaseModel):
    employee_name: str
    leave_type: str
    duration_days: int
    current_balance: int

def check_rate_limit():
    """Simple rate limiting"""
    now = time.time()
    request_times.append(now)

    # Count requests in last minute
    recent = [t for t in request_times if now - t < 60]
    if len(recent) > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.post("/analyze-leave")
async def analyze_leave(request: LeaveRequest, api_key: str = Header(None)):
    """Analyze leave request using AI"""

    # Simple API key auth
    if api_key != "your-secret-key":
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Rate limiting
    check_rate_limit()

    # Call Ollama
    prompt = f"""Analyze this leave request:
Employee: {request.employee_name}
Type: {request.leave_type}
Duration: {request.duration_days} days
Balance: {request.current_balance} days

Is this within policy? Answer YES or NO with reason."""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    return {
        "analysis": response.json()['response'],
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "model": "llama3.2:3b"}

# Run with: uvicorn model_server:app --host 0.0.0.0 --port 8000
```

Test the API:

```bash
# Start server
uvicorn model_server:app --reload

# Test with curl
curl -X POST "http://localhost:8000/analyze-leave" \
  -H "api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_name": "John Doe",
    "leave_type": "annual_leave",
    "duration_days": 8,
    "current_balance": 21
  }'
```

### What You'll Learn:
- REST API design for ML models
- Authentication and security
- Rate limiting and abuse prevention
- Production deployment patterns

**Time:** 2-3 hours
**Cost:** ~$0.20-0.30
**Value:** ⭐⭐⭐⭐ (Production skill)

---

## 📊 Complete Learning Roadmap

### Day 1 (3-4 hours): Foundation
1. Multi-model comparison (2 hrs)
2. Quantization testing (1 hr)
3. Performance benchmarking (1 hr)

**Cost:** ~$0.30-0.40
**Skills:** Model selection, optimization basics

### Day 2 (4-5 hours): Advanced
1. RAG system building (3 hrs)
2. Prompt engineering workshop (2 hrs)

**Cost:** ~$0.40-0.50
**Skills:** RAG, retrieval, prompt optimization

### Day 3 (5-6 hours): Expert
1. Fine-tuning workshop (4 hrs)
2. Model serving API (2 hrs)

**Cost:** ~$0.50-0.60
**Skills:** Fine-tuning, production deployment

**Total Investment:** ~10-15 hours, $1.20-1.50

---

## 🎁 Bonus Experiments

### 7. Vision Models (If server has GPU)
```bash
ollama pull llava:7b        # Image understanding
ollama pull bakllava:7b     # Another vision model

# Test with images
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llava",
  "prompt": "What is in this image?",
  "images": ["base64_encoded_image"]
}'
```

### 8. Code Generation Models
```bash
ollama pull codellama:7b
ollama pull deepseek-coder:6.7b
ollama pull codegemma:7b

# Test code generation
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "codellama:7b",
  "prompt": "Write a Python function to validate email addresses"
}'
```

### 9. Multilingual Models
```bash
ollama pull aya:8b           # 101 languages
ollama pull command-r:35b    # Multilingual

# Test translation
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "aya:8b",
  "prompt": "Translate to Spanish: Hello, how are you?"
}'
```

---

## 📈 Skill Development Path

### Beginner → Intermediate (Week 1)
- ✅ Run multiple models
- ✅ Understand quantization
- ✅ Measure performance
- ✅ Build basic RAG system

### Intermediate → Advanced (Week 2)
- ✅ Fine-tune custom models
- ✅ Deploy production APIs
- ✅ Optimize prompts
- ✅ Handle concurrent requests

### Advanced → Expert (Week 3+)
- ✅ Multi-GPU training
- ✅ Model compression
- ✅ Custom architectures
- ✅ A/B testing frameworks

---

## 💰 Cost Breakdown

| Activity | Time | Cost @ $0.09/hr | Value |
|----------|------|-----------------|-------|
| Multi-model testing | 2 hrs | $0.18 | ⭐⭐⭐⭐⭐ |
| Fine-tuning | 4 hrs | $0.36 | ⭐⭐⭐⭐⭐ |
| RAG system | 3 hrs | $0.27 | ⭐⭐⭐⭐⭐ |
| API deployment | 2 hrs | $0.18 | ⭐⭐⭐⭐ |
| Benchmarking | 1 hr | $0.09 | ⭐⭐⭐⭐ |
| **Total** | **12 hrs** | **$1.08** | **Priceless** |

**ROI:** Learn enterprise AI skills for the cost of a coffee!

---

## 🎯 My Top 3 Recommendations for You

### 1. ⭐⭐⭐⭐⭐ Multi-Model Comparison
**Why:** Understand which models work best for different tasks
**Time:** 2 hours
**Cost:** $0.18
**What you'll learn:** Model selection, accuracy vs speed tradeoffs

### 2. ⭐⭐⭐⭐⭐ Fine-Tuning Workshop
**Why:** Turn 67% accuracy → 95% accuracy
**Time:** 4 hours
**Cost:** $0.36
**What you'll learn:** How to customize models for your data

### 3. ⭐⭐⭐⭐⭐ RAG System Building
**Why:** Build real-world document Q&A systems
**Time:** 3 hours
**Cost:** $0.27
**What you'll learn:** Production-ready AI applications

**Total:** 9 hours, $0.81, skills worth $10,000+ in the job market

---

## 📥 Quick Start Package

I can create a complete package with all these experiments ready to run. Would you like me to:

1. ✅ Create all test scripts
2. ✅ Generate training data
3. ✅ Write deployment instructions
4. ✅ Include benchmarking tools

Just upload to GPU server and start learning!

---

## 🚀 Next Steps

**To get started:**

```bash
# 1. Rent GPU server (Vast.ai RTX 4000 @ $0.09/hr)
# 2. Upload scripts (I'll create them for you)
# 3. Run experiments one by one
# 4. Learn enterprise AI skills for < $2!
```

**Want me to create the complete experiment package?** I can generate all the scripts, data, and instructions so you can just run them on the GPU server.
