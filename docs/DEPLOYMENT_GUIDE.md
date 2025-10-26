# Deployment Guide: GPU Server Setup

## Quick Answer

**Should you deploy GPT-4 to GPU server?**
- **YES, but...** you don't need GPU for GPT-4 (it just calls OpenAI API)
- **Better idea:** Deploy BOTH and compare performance

---

## Deployment Options

### Option 1: GPT-4 Only (OpenAI API)

**What to upload:**
```bash
leave_management_agent.py       # GPT-4 version
leave_app_demo.py               # Demo script
hr_knowledge_base.json          # HR policies
.env                            # OPENAI_API_KEY
test_gpt4_vs_ollama.py         # Optional: comparison test
```

**Setup on GPU server:**
```bash
# Install Python dependencies
pip install openai python-dotenv

# Upload .env file with your API key
# Make sure it contains: OPENAI_API_KEY=sk-proj-...

# Run demo
python3 leave_app_demo.py
```

**Cost:** ~$0.01-0.02 per request
**GPU Usage:** None (doesn't use GPU)
**Accuracy:** 100%

---

### Option 2: Ollama Only (Local GPU)

**What to upload:**
```bash
leave_management_agent_ollama.py  # Ollama version
leave_app_demo_ollama.py          # Ollama demo
hr_knowledge_base.json            # HR policies
test_improved_ollama.py           # Optional: accuracy test
```

**Setup on GPU server:**
```bash
# Install Ollama (if not already)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &

# Pull Llama 3.2
ollama pull llama3.2:latest

# Verify GPU is detected
nvidia-smi

# Run demo
python3 leave_app_demo_ollama.py
```

**Cost:** $0.00 (free)
**GPU Usage:** 3-4GB VRAM, 50-90% utilization
**Accuracy:** ~67% (needs fine-tuning)

---

### Option 3: 🏆 Hybrid (RECOMMENDED)

Deploy **both** systems and compare them side-by-side!

**What to upload:**
```bash
# GPT-4 files
leave_management_agent.py
leave_app_demo.py

# Ollama files
leave_management_agent_ollama.py
leave_app_demo_ollama.py

# Shared files
hr_knowledge_base.json
.env                           # For GPT-4 API key

# Test & comparison
test_gpt4_vs_ollama.py
test_improved_ollama.py
```

**Benefits:**
- ✅ Test both on same hardware
- ✅ Compare accuracy in real-time
- ✅ Benchmark GPU vs API performance
- ✅ Decide which to use for production

**Setup:**
```bash
# Install everything
pip install openai python-dotenv
ollama serve &
ollama pull llama3.2:latest

# Run comparison test
python3 test_gpt4_vs_ollama.py

# Run both demos
python3 leave_app_demo.py          # GPT-4
python3 leave_app_demo_ollama.py   # Ollama
```

---

## File Upload Commands

### From Your Mac to GPU Server

**Using SCP:**
```bash
# Replace with your actual server details
SERVER_IP="your.server.ip"
SERVER_PORT="22"
SERVER_USER="root"

# Upload GPT-4 files
scp -P $SERVER_PORT \
  leave_management_agent.py \
  leave_app_demo.py \
  hr_knowledge_base.json \
  .env \
  $SERVER_USER@$SERVER_IP:/app/

# Upload Ollama files
scp -P $SERVER_PORT \
  leave_management_agent_ollama.py \
  leave_app_demo_ollama.py \
  $SERVER_USER@$SERVER_IP:/app/

# Upload test scripts
scp -P $SERVER_PORT \
  test_gpt4_vs_ollama.py \
  test_improved_ollama.py \
  $SERVER_USER@$SERVER_IP:/app/
```

**For Vast.ai:**
```bash
# Get connection details from Vast.ai dashboard
# Example:
scp -P 12345 \
  leave_management_agent*.py \
  leave_app_demo*.py \
  hr_knowledge_base.json \
  .env \
  root@ssh.vast.ai:/root/
```

**For RunPod:**
```bash
# Get connection from RunPod dashboard
scp -P 54321 \
  leave_management_agent*.py \
  leave_app_demo*.py \
  hr_knowledge_base.json \
  .env \
  root@runpod-ip:/workspace/
```

---

## Quick Start Script

Save this as `deploy_to_server.sh`:

```bash
#!/bin/bash

# Configuration
SERVER="root@YOUR_SERVER_IP"
PORT="22"
REMOTE_DIR="/app"

echo "🚀 Deploying Leave Management System to GPU Server..."

# Create remote directory
ssh -p $PORT $SERVER "mkdir -p $REMOTE_DIR"

# Upload all necessary files
echo "📤 Uploading files..."
scp -P $PORT \
  leave_management_agent.py \
  leave_management_agent_ollama.py \
  leave_app_demo.py \
  leave_app_demo_ollama.py \
  hr_knowledge_base.json \
  .env \
  test_gpt4_vs_ollama.py \
  test_improved_ollama.py \
  $SERVER:$REMOTE_DIR/

echo "✅ Files uploaded!"

# Setup server
echo "🔧 Setting up server..."
ssh -p $PORT $SERVER << 'EOF'
cd /app

# Install Python dependencies
pip install openai python-dotenv

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama
ollama serve &
sleep 5

# Pull Llama 3.2
ollama pull llama3.2:latest

# Verify GPU
nvidia-smi

echo "✅ Setup complete!"
EOF

echo "🎉 Deployment complete!"
echo ""
echo "To test, SSH into server and run:"
echo "  python3 /app/test_gpt4_vs_ollama.py"
```

**Make it executable and run:**
```bash
chmod +x deploy_to_server.sh
./deploy_to_server.sh
```

---

## What Each Option Costs on GPU Server

### GPU Server Costs
| Provider | GPU | Cost/Hour |
|----------|-----|-----------|
| Vast.ai | RTX 4000 | $0.09 |
| RunPod | RTX A4000 | $0.19 |

### Per-Request Costs

**Option 1: GPT-4 on GPU Server**
- Server cost: $0.09/hr ÷ 3600 sec = $0.000025/sec
- API cost: ~$0.01-0.02 per request
- **Total: ~$0.01-0.02 per request** (API cost dominates)
- **Does NOT use GPU** (wasting server cost!)

**Option 2: Ollama on GPU Server**
- Server cost: $0.09/hr ÷ 3600 sec = $0.000025/sec
- Inference time: ~2 sec per request
- **Total: ~$0.00005 per request** (essentially free)
- **USES GPU** (makes sense to rent GPU)

---

## My Recommendation

### For Testing (Next 10 hours):

✅ **Deploy BOTH to GPU server**

**Why?**
1. Test Ollama with GPU acceleration (free, 2-4x faster than CPU)
2. Compare accuracy with GPT-4 on same test cases
3. Measure real-world performance
4. Decide which to use for production

**Cost:** $0.90 for 10 hours on Vast.ai

### For Production:

**If accuracy is critical (HR, legal, compliance):**
→ ✅ **Use GPT-4** (don't need GPU server, can run anywhere)

**If cost is critical and you can fine-tune:**
→ ✅ **Use Ollama on GPU** (but only after achieving 95%+ accuracy)

---

## Testing Plan on GPU Server

Once deployed, run these tests:

```bash
# 1. Test GPT-4 accuracy
python3 test_gpt4_vs_ollama.py
# Expected: 100% accuracy, ~2-3 sec per request

# 2. Test Ollama accuracy
python3 test_improved_ollama.py
# Expected: ~67% accuracy, ~1-2 sec per request (with GPU)

# 3. Monitor GPU usage
watch -n 1 nvidia-smi
# Ollama should show 50-90% GPU utilization
# GPT-4 should show 0% GPU utilization

# 4. Run full demos
python3 leave_app_demo.py          # GPT-4
python3 leave_app_demo_ollama.py   # Ollama
```

---

## Decision Matrix

| Your Priority | Recommended Option | Where to Run |
|--------------|-------------------|--------------|
| **Maximum Accuracy** | GPT-4 | Anywhere (laptop, cloud, server) |
| **Minimum Cost** | Ollama (after fine-tuning) | GPU server |
| **Privacy (no external APIs)** | Ollama | GPU server |
| **Quick Testing** | Both | GPU server for 10 hours |
| **Production (critical decisions)** | GPT-4 | Cloud API (no GPU needed) |

---

## Next Steps

**For Your Use Case (Testing on GPU server):**

1. ✅ **Upload both versions** (GPT-4 + Ollama)
2. ✅ **Run comparison tests**
3. ✅ **Measure GPU utilization** with Ollama
4. ✅ **Compare costs** (API vs GPU)
5. ✅ **Decide** based on accuracy needs

**Commands:**
```bash
# Upload files
scp -P PORT leave_*.py hr_knowledge_base.json .env user@server:/app/

# SSH to server
ssh -p PORT user@server

# Run tests
cd /app
python3 test_gpt4_vs_ollama.py
```

---

## Files Summary

### Must Upload for GPT-4:
- [leave_management_agent.py](leave_management_agent.py) ✅
- [leave_app_demo.py](leave_app_demo.py) ✅
- [hr_knowledge_base.json](hr_knowledge_base.json) ✅
- [.env](.env) ✅ (contains OPENAI_API_KEY)

### Must Upload for Ollama:
- [leave_management_agent_ollama.py](leave_management_agent_ollama.py) ✅
- [leave_app_demo_ollama.py](leave_app_demo_ollama.py) ✅
- [hr_knowledge_base.json](hr_knowledge_base.json) ✅

### Optional (for testing):
- [test_gpt4_vs_ollama.py](test_gpt4_vs_ollama.py) 📊
- [test_improved_ollama.py](test_improved_ollama.py) 📊
- [GPT4_VS_OLLAMA_REPORT.md](GPT4_VS_OLLAMA_REPORT.md) 📄

---

## Security Note

⚠️ **IMPORTANT:** Your `.env` file contains your OpenAI API key!

```bash
# Before uploading, verify .env has correct key
cat .env
# Should show: OPENAI_API_KEY=sk-proj-...

# After uploading to server, secure it
ssh user@server
chmod 600 /app/.env  # Only owner can read/write
```

Don't commit `.env` to git or share it publicly!

---

**Ready to deploy?** Just run:
```bash
scp -P YOUR_PORT leave_*.py hr_knowledge_base.json .env user@server:/app/
```
