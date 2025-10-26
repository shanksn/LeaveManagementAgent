# Secure Deployment Guide: Protecting Your API Keys

## 🚨 Security Warning

**NEVER upload your OpenAI API key to a shared GPU server!**

Shared environments (Vast.ai, RunPod community instances, etc.) are NOT secure for secrets:
- ❌ Other users may have access
- ❌ Admins can read your files
- ❌ Logs may capture your keys
- ❌ Compromised server = compromised key
- ❌ Financial liability (someone uses your key = you pay!)

---

## ✅ Safe Alternative 1: Use Ollama Only (RECOMMENDED for GPU server)

**Best option for shared GPU environments**

### Why This is Safe:
- ✅ No API keys needed
- ✅ Runs 100% locally on GPU
- ✅ No internet required after model download
- ✅ Your data never leaves the server
- ✅ Zero financial risk from key theft

### What to Upload:
```bash
# Only these files - NO .env!
leave_management_agent_ollama.py
leave_app_demo_ollama.py
hr_knowledge_base.json
test_improved_ollama.py
```

### Deployment Commands:
```bash
# Upload files (NO .env!)
scp -P PORT \
  leave_management_agent_ollama.py \
  leave_app_demo_ollama.py \
  hr_knowledge_base.json \
  test_improved_ollama.py \
  root@SERVER_IP:/app/

# SSH to server
ssh -p PORT root@SERVER_IP

# Setup Ollama
cd /app
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:latest

# Run demo (no API key needed!)
python3 leave_app_demo_ollama.py
```

### Limitations:
- ⚠️ 67% accuracy (vs GPT-4's 100%)
- ⚠️ Needs fine-tuning for production
- ✅ But SAFE and FREE!

---

## ✅ Safe Alternative 2: Use GPT-4 from Your Local Machine

**Best option if you need GPT-4's accuracy**

### Why This is Safe:
- ✅ API key stays on YOUR computer
- ✅ Full control over .env file
- ✅ No exposure to shared servers

### Setup:
```bash
# Run everything locally (on your Mac)
cd /Users/shankar/Documents/LlamaParsing

# Your .env is safe here
python3 leave_app_demo.py
python3 test_gpt4_vs_ollama.py
```

### When to Use:
- Production deployments (your own server)
- Local testing and development
- When you need 100% accuracy

### Limitations:
- ❌ Doesn't use GPU server you're paying for
- ❌ But your API key is SAFE!

---

## ✅ Safe Alternative 3: SSH Tunnel (Advanced)

**Use GPT-4 locally, connect to GPU server's Ollama**

This lets you compare both safely:

### Setup:

**Step 1: Start Ollama on GPU server**
```bash
ssh -p PORT root@SERVER_IP
ollama serve
# Keep this terminal open
```

**Step 2: Create SSH tunnel from your Mac**
```bash
# From your Mac, open new terminal
ssh -p PORT -L 11434:localhost:11434 root@SERVER_IP
# This forwards Ollama port to your local machine
# Keep this terminal open
```

**Step 3: Run tests from your Mac**
```bash
# From your Mac, in another terminal
cd /Users/shankar/Documents/LlamaParsing

# Test GPT-4 (uses your local .env - SAFE!)
python3 leave_app_demo.py

# Test Ollama (connects to GPU server via tunnel - SAFE!)
python3 leave_app_demo_ollama.py
# This connects to localhost:11434, which tunnels to GPU server
```

### Benefits:
- ✅ API key never leaves your Mac
- ✅ Ollama runs on GPU server (fast)
- ✅ You can compare both models
- ✅ Completely secure

---

## ✅ Safe Alternative 4: Environment Variable (Less Safe, but Better)

**If you MUST run GPT-4 on shared server**

Instead of uploading .env file, set environment variable in your SSH session only.

### Setup:

```bash
# SSH to server
ssh -p PORT root@SERVER_IP

# Set API key in this session ONLY (not saved to disk)
export OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"

# Run demo
python3 /app/leave_app_demo.py

# When you disconnect, the key is gone from memory
```

### Slightly Better Because:
- ✅ Key not saved to disk (harder to find)
- ✅ Only exists in your session
- ❌ Still visible to admins via process monitoring
- ❌ Still risky on shared servers

### Important Security Steps:
```bash
# Don't save key in bash history
export HISTCONTROL=ignorespace
 export OPENAI_API_KEY="sk-..."  # Note the space before 'export'
# OR
unset HISTFILE  # Disable history for this session

# After running, immediately unset
unset OPENAI_API_KEY
```

---

## ✅ Safe Alternative 5: Create a Read-Only Test API Key

**If you absolutely need GPT-4 on shared server**

### Step 1: Create Restricted API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Set permissions:
   - Name: "GPU Server Testing - Limited"
   - Permissions: **Read-only** or **Limited usage**
   - Rate limit: **10 requests/minute**
   - Spend limit: **$5 maximum**
4. Copy the key

### Step 2: Use This Key on Server

```bash
# Upload with LIMITED key only
echo "OPENAI_API_KEY=sk-proj-LIMITED-KEY" > .env
scp -P PORT .env root@SERVER_IP:/app/

# Delete local copy
rm .env
```

### Benefits:
- ✅ If stolen, limited damage ($5 max)
- ✅ Can revoke anytime
- ✅ Can monitor usage closely

### Important:
- ⚠️ Still not ideal for shared servers
- ⚠️ Better than main key, but Ollama is safer

---

## 🎯 My Recommendation for Your Situation

### For GPU Server Testing:

**Use Ollama Only (No API Keys)**

```bash
# 1. Upload ONLY Ollama files
scp -P PORT \
  leave_management_agent_ollama.py \
  leave_app_demo_ollama.py \
  hr_knowledge_base.json \
  root@SERVER_IP:/app/

# 2. Setup on server
ssh -p PORT root@SERVER_IP
ollama serve &
ollama pull llama3.2:latest

# 3. Test GPU performance
python3 /app/leave_app_demo_ollama.py
watch -n 1 nvidia-smi  # Monitor GPU usage
```

**Benefits:**
- ✅ 100% secure (no API keys)
- ✅ Tests GPU acceleration
- ✅ Free (no API costs)
- ✅ Learn about Ollama performance
- ✅ No financial risk

**For GPT-4 Testing:**

Run on your local Mac where .env is safe:
```bash
# On your Mac
cd /Users/shankar/Documents/LlamaParsing
python3 test_gpt4_vs_ollama.py
```

---

## 🔐 Security Best Practices

### 1. Never Upload These Files to Shared Servers:
- ❌ .env
- ❌ credentials.json
- ❌ config files with secrets
- ❌ private keys (.pem, .key files)

### 2. Always Check File Permissions:
```bash
# If you MUST upload secrets (not recommended)
chmod 600 /app/.env  # Only you can read
# But admins can still access!
```

### 3. Use .gitignore:
```bash
# In your project
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "credentials.json" >> .gitignore
```

### 4. Revoke Keys After Testing:
```bash
# After GPU server testing, revoke any keys used
# Go to: https://platform.openai.com/api-keys
# Click "Revoke" on any keys used on shared servers
```

### 5. Monitor Usage:
```bash
# Check OpenAI usage daily during testing
# https://platform.openai.com/usage
# Look for unexpected spikes
```

---

## 📊 Comparison: Safe vs Unsafe Approaches

| Approach | Security | Cost | GPU Usage | GPT-4 Access | Recommended? |
|----------|----------|------|-----------|--------------|--------------|
| **Upload .env to shared server** | ❌ UNSAFE | $$ + GPU | Wasted | ✅ | ❌ NO |
| **Ollama only on GPU server** | ✅ SAFE | GPU only | ✅ Used | ❌ | ✅ YES |
| **GPT-4 on local Mac** | ✅ SAFE | API only | ❌ None | ✅ | ✅ YES |
| **SSH Tunnel (both)** | ✅ SAFE | API + GPU | ✅ Used | ✅ | ✅ YES (advanced) |
| **Limited API key** | ⚠️ Risky | Capped | Wasted | ✅ | ⚠️ Maybe |
| **Env var (no file)** | ⚠️ Risky | $$ + GPU | Wasted | ✅ | ⚠️ Last resort |

---

## 🚀 Step-by-Step: Secure Deployment

### Option A: Ollama on GPU Server (Recommended)

```bash
# 1. Upload files (NO .env!)
scp -P 12345 \
  leave_management_agent_ollama.py \
  leave_app_demo_ollama.py \
  hr_knowledge_base.json \
  root@vast.ai:/app/

# 2. SSH and setup
ssh -p 12345 root@vast.ai
cd /app
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:latest

# 3. Test
python3 leave_app_demo_ollama.py

# 4. Monitor GPU
nvidia-smi
```

**Result:**
- ✅ Secure (no secrets uploaded)
- ✅ Uses GPU (what you're paying for)
- ✅ Free inference (no API costs)

### Option B: SSH Tunnel (Advanced, Both Models)

```bash
# Terminal 1 (GPU server) - Start Ollama
ssh -p 12345 root@vast.ai
ollama serve

# Terminal 2 (your Mac) - Create tunnel
ssh -p 12345 -L 11434:localhost:11434 root@vast.ai

# Terminal 3 (your Mac) - Run tests
cd /Users/shankar/Documents/LlamaParsing
python3 test_gpt4_vs_ollama.py
# GPT-4: Uses local .env (safe!)
# Ollama: Connects via tunnel to GPU server
```

**Result:**
- ✅ Secure (API key stays local)
- ✅ Uses GPU for Ollama
- ✅ Can compare both models

---

## ⚠️ What If You Already Uploaded Your Key?

**Take these steps IMMEDIATELY:**

### 1. Revoke the Key
```bash
# Go to: https://platform.openai.com/api-keys
# Find your key and click "Revoke"
# This invalidates it immediately
```

### 2. Delete from Server
```bash
ssh -p PORT root@SERVER_IP
rm /app/.env
rm ~/.bash_history  # Remove from history
history -c          # Clear current history
```

### 3. Create New Key
```bash
# Create a new key for local use only
# Never upload this one!
```

### 4. Check for Unauthorized Usage
```bash
# Visit: https://platform.openai.com/usage
# Look for suspicious activity
# Check if usage matches your testing
```

---

## 📋 Checklist: Before Uploading Anything

- [ ] Does this file contain secrets? (.env, keys, credentials)
- [ ] Is the server truly private (owned by you) or shared?
- [ ] Can I use a local-only alternative (Ollama)?
- [ ] Can I run this on my local machine instead?
- [ ] If I must use secrets, is there a limited/test key option?
- [ ] Have I set up monitoring for unusual usage?
- [ ] Do I have a plan to revoke keys after testing?

**If you answered "yes" to secrets + shared server → DON'T UPLOAD!**

---

## 🎯 Final Recommendation

**For your GPU server testing:**

1. ✅ **Use Ollama on GPU server** (no API keys needed)
   - Test GPU acceleration
   - Measure accuracy (~67%)
   - Learn about fine-tuning needs
   - **Cost:** $0.09/hr on Vast.ai
   - **Security:** Perfect (no secrets)

2. ✅ **Use GPT-4 on your Mac** (keep .env local)
   - Test accuracy (100%)
   - Compare with Ollama results
   - **Cost:** $0.01-0.02 per test
   - **Security:** Perfect (local only)

3. ❌ **Don't upload .env to shared GPU server**
   - Not worth the risk
   - You're not using GPU anyway with GPT-4
   - Keep secrets local!

---

## 📞 Questions to Ask Before Uploading

**Ask your GPU provider:**
1. "Is this a shared server or dedicated instance?"
2. "Can other users access my files?"
3. "Do admins have access to user data?"
4. "Are files backed up? Where?"

**If ANY answer is "yes" or "maybe" → Don't upload secrets!**

---

## Summary

🚫 **DON'T:** Upload .env with OPENAI_API_KEY to shared GPU server
✅ **DO:** Use Ollama on GPU server (no API keys needed)
✅ **DO:** Run GPT-4 tests on your local Mac (keep .env safe)
✅ **DO:** Use SSH tunnels if you need both (advanced)

**Your API key = Your money. Protect it like a credit card!**
