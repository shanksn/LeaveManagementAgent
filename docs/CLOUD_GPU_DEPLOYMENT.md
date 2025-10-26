# Cloud GPU Deployment Guide - Ollama Leave Management System

## 🎯 Goal: Test Ollama Leave Management System on GPU VM at Lowest Cost

---

## 💰 Cost Comparison Summary

### Llama 3.2 3B Requirements
- **VRAM needed**: ~3.4 GB
- **RAM needed**: 8 GB
- **Storage**: 10 GB
- **Recommended GPU**: T4 (16GB VRAM) or RTX 4000 (8GB VRAM)

### Provider Pricing (Sorted by Cost)

| Provider | GPU Type | VRAM | Cost/Hour | Monthly (24/7) | Notes |
|----------|----------|------|-----------|----------------|-------|
| **Vast.ai** | RTX 4000 | 8GB | **$0.09** | $65 | ⭐ Cheapest spot |
| **TensorDock** | T4 | 16GB | **$0.12** | $86 | Very competitive |
| **RunPod** | RTX A4000 | 16GB | **$0.19** | $137 | Good reliability |
| **GCP Spot** | T4 | 16GB | **$0.09-0.27** | $65-195 | Can be preempted |
| **AWS Spot** | T4 | 16GB | **$0.09-0.30** | $65-216 | Can be preempted |
| **Azure Spot** | T4 | 16GB | **$0.09-0.27** | $65-195 | Can be preempted |
| **Lambda Labs** | RTX A4000 | 16GB | **$0.50** | $360 | Easy to use |
| **AWS On-demand** | T4 | 16GB | **$0.53** | $382 | Stable but expensive |
| **GCP On-demand** | L4 | 24GB | **$0.60** | $432 | Latest GPU |

### 💡 Recommended Options

**For Testing (1-10 hours):**
- **Vast.ai** - RTX 4000 @ **$0.09/hr** ✅ BEST VALUE
- **TensorDock** - T4 @ $0.12/hr
- **RunPod** - RTX A4000 @ $0.19/hr

**For Production (reliable):**
- **RunPod** - Stable, good support
- **GCP Spot** - Reliable spot instances

**Cost for 10 hours of testing:**
- Vast.ai: $0.90
- TensorDock: $1.20
- RunPod: $1.90

---

## 🚀 Option 1: Vast.ai (CHEAPEST - $0.09/hr)

### Why Vast.ai?
✅ Cheapest GPU pricing
✅ Pay-per-second billing
✅ No commitment
✅ Easy setup
❌ Community-run (less reliable than AWS/GCP)

### Step-by-Step Setup

#### 1. Create Account
```bash
# Visit https://vast.ai
# Sign up and add $10 credit (enough for 100+ hours)
```

#### 2. Find GPU Instance
1. Go to "Search" → "GPU Instances"
2. Filters:
   - GPU Type: RTX 4000 or T4
   - VRAM: ≥ 8GB
   - RAM: ≥ 8GB
   - Sort by: "$/hr (cheapest first)"
3. Look for **$0.09-0.15/hr** instances

#### 3. Launch Instance
```bash
# Click "Rent" on cheapest available instance
# Select template: "PyTorch" or "Ubuntu 22.04"
# SSH enabled: Yes
# Disk space: 20GB
```

#### 4. SSH into Instance
```bash
# Copy SSH command from Vast.ai dashboard
ssh -p PORT_NUMBER root@IP_ADDRESS -L 8080:localhost:8080
```

#### 5. Install Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve &

# Pull Llama 3.2 model
ollama pull llama3.2:latest

# Verify GPU is detected
nvidia-smi
```

#### 6. Deploy Leave Management System
```bash
# Install dependencies
apt update && apt install -y python3 python3-pip git

# Clone your code (or upload via SCP)
mkdir -p /app
cd /app

# Upload your files (from your local machine)
# Run this on YOUR LOCAL MACHINE:
# scp -P PORT_NUMBER leave_management_agent_ollama.py root@IP_ADDRESS:/app/
# scp -P PORT_NUMBER leave_app_demo_ollama.py root@IP_ADDRESS:/app/
# scp -P PORT_NUMBER hr_knowledge_base.json root@IP_ADDRESS:/app/
```

#### 7. Run the Demo
```bash
cd /app
python3 leave_app_demo_ollama.py
```

#### 8. Test GPU Acceleration
```bash
# Monitor GPU usage while running
watch -n 1 nvidia-smi

# You should see:
# - GPU Memory Used: ~3-4GB
# - GPU Utilization: 50-90% during inference
```

#### 9. Stop Instance (Save Money!)
```bash
# When done testing, go to Vast.ai dashboard
# Click "Destroy Instance"
# You're only charged for actual usage time!
```

### Cost Estimate
- **Testing (10 hours)**: $0.90
- **Full day**: $2.16
- **Week of testing (8 hrs/day)**: $5.04

---

## 🚀 Option 2: RunPod (RELIABLE - $0.19/hr)

### Why RunPod?
✅ More reliable than Vast.ai
✅ Better support
✅ Easy dashboard
✅ Good for longer tests
❌ Slightly more expensive

### Step-by-Step Setup

#### 1. Create Account
```bash
# Visit https://runpod.io
# Sign up and add $10 credit
```

#### 2. Launch GPU Pod
1. Click "Deploy" → "GPU Instances"
2. Select: **RTX A4000** (16GB VRAM, $0.19/hr)
3. Template: "PyTorch 2.0" or "Ubuntu 22.04"
4. Volume: 20GB
5. Click "Deploy"

#### 3. Connect via SSH
```bash
# Get SSH command from RunPod dashboard
ssh root@RUNPOD_IP -p RUNPOD_PORT
```

#### 4. Install Ollama & Deploy
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:latest

# Install Python
apt update && apt install -y python3 python3-pip

# Upload your files (from local machine)
# scp -P RUNPOD_PORT leave_*.py hr_knowledge_base.json root@RUNPOD_IP:/root/

# Run demo
cd /root
python3 leave_app_demo_ollama.py
```

#### 5. Use Web Terminal (Alternative)
RunPod provides a web terminal - no SSH needed!
1. Click "Connect" → "Start Web Terminal"
2. Run all commands in browser

### Cost Estimate
- **Testing (10 hours)**: $1.90
- **Full day**: $4.56
- **Week (8 hrs/day)**: $10.64

---

## 🚀 Option 3: GCP Spot Instances (SCALABLE - $0.10-0.27/hr)

### Why GCP?
✅ Enterprise-grade reliability
✅ Easy to scale
✅ Good for production testing
❌ More complex setup
❌ Spot instances can be preempted

### Step-by-Step Setup

#### 1. Prerequisites
```bash
# Install gcloud CLI
# macOS:
brew install google-cloud-sdk

# Linux:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### 2. Create VM with T4 GPU
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Create spot instance with T4 GPU
gcloud compute instances create ollama-test \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --provisioning-model=SPOT \
  --maintenance-policy=TERMINATE \
  --metadata=startup-script='#!/bin/bash
    # Install NVIDIA drivers
    curl -fsSL https://nvidia.github.io/nvidia-docker/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-docker.gpg
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
      sed "s#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-docker.gpg] https://#g" | \
      sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    apt-get update
    apt-get install -y nvidia-driver-535
    '
```

#### 3. SSH into Instance
```bash
# SSH
gcloud compute ssh ollama-test --zone=us-central1-a

# Verify GPU
nvidia-smi
```

#### 4. Install Ollama & Deploy
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:latest

# Install Python
sudo apt update && sudo apt install -y python3 python3-pip

# Upload files (from your local machine)
gcloud compute scp leave_*.py hr_knowledge_base.json \
  ollama-test:/home/$USER/ --zone=us-central1-a

# Run demo
python3 leave_app_demo_ollama.py
```

#### 5. Stop Instance (Save Money!)
```bash
# Stop (preserves data, minimal charge)
gcloud compute instances stop ollama-test --zone=us-central1-a

# Delete (no charge)
gcloud compute instances delete ollama-test --zone=us-central1-a
```

### Cost Estimate (Spot Pricing)
- **T4 GPU**: ~$0.10/hr
- **n1-standard-4**: ~$0.10/hr
- **Total**: ~$0.20/hr (can spike to $0.27/hr)
- **Testing (10 hours)**: ~$2.00

---

## 🐳 Docker Deployment (ALL PROVIDERS)

### Create Dockerfile
```dockerfile
# Dockerfile
FROM nvidia/cuda:12.2.0-base-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy application files
WORKDIR /app
COPY leave_management_agent_ollama.py .
COPY leave_app_demo_ollama.py .
COPY hr_knowledge_base.json .

# Pull Llama model (done at runtime to save image size)
# We'll do this in entrypoint

# Create entrypoint script
COPY <<EOF /entrypoint.sh
#!/bin/bash
# Start Ollama server
ollama serve &
sleep 5

# Pull model if not exists
ollama pull llama3.2:latest

# Run demo
python3 /app/leave_app_demo_ollama.py

# Keep container running for interactive use
tail -f /dev/null
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### Build and Run
```bash
# Build image
docker build -t ollama-leave-management .

# Run on any cloud provider with GPU
docker run --gpus all -it ollama-leave-management
```

---

## 📊 Performance Benchmarks

### Expected Performance on Different GPUs

| GPU | VRAM | Tokens/sec | Response Time | Cost/Hour |
|-----|------|------------|---------------|-----------|
| **RTX 4000** | 8GB | 40-50 | 1.5-2s | $0.09 |
| **T4** | 16GB | 30-40 | 2-3s | $0.10 |
| **RTX A4000** | 16GB | 50-60 | 1-1.5s | $0.19 |
| **L4** | 24GB | 60-80 | 1-1.5s | $0.60 |
| **A100** | 40GB | 100-150 | 0.5-1s | $1.20 |

**Recommendation**: RTX 4000 or T4 is perfect for Llama 3.2 3B - no need for expensive GPUs!

---

## ✅ Quick Start Checklist

### Before You Start
- [ ] Choose provider (Vast.ai recommended for testing)
- [ ] Create account and add $10 credit
- [ ] Have your files ready: `leave_management_agent_ollama.py`, `leave_app_demo_ollama.py`, `hr_knowledge_base.json`

### On Cloud VM
- [ ] Launch GPU instance (RTX 4000 or T4)
- [ ] SSH into instance
- [ ] Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] Start Ollama: `ollama serve &`
- [ ] Pull model: `ollama pull llama3.2:latest`
- [ ] Verify GPU: `nvidia-smi`
- [ ] Upload files via SCP
- [ ] Run demo: `python3 leave_app_demo_ollama.py`
- [ ] Monitor GPU: `watch -n 1 nvidia-smi`
- [ ] Test all 3 improvements (prompts, GPU, accuracy)
- [ ] Stop/destroy instance when done

---

## 💡 Cost Optimization Tips

### 1. Use Spot/Preemptible Instances
- Save 60-90% compared to on-demand
- Good for testing (acceptable if interrupted)

### 2. Stop When Not Using
```bash
# Most providers charge per minute/second
# Stop instance during breaks
# Vast.ai: Destroy instance (data is temporary anyway)
# GCP/AWS: Stop instance (data preserved)
```

### 3. Use Smallest GPU That Works
- Llama 3.2 3B needs only 3.4GB VRAM
- Don't pay for A100 (40GB) when T4 (16GB) works fine!

### 4. Batch Your Testing
- Plan your tests in advance
- Run all tests in one session
- Minimize idle time

### 5. Use Community Providers
- Vast.ai, TensorDock are 3-5x cheaper
- Acceptable for testing (not production)

---

## 🔧 Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi

# If not found, install drivers
# Ubuntu:
sudo apt update
sudo apt install -y nvidia-driver-535

# Verify Ollama sees GPU
ollama run llama3.2:latest "test" --verbose
# Should show GPU layers loaded
```

### Ollama Not Starting
```bash
# Check if port 11434 is in use
lsof -i :11434

# Kill existing Ollama
pkill ollama

# Restart
ollama serve &
```

### Out of Memory
```bash
# Check GPU memory
nvidia-smi

# If using 100% VRAM, you need larger GPU
# Or reduce num_predict in code
# Edit leave_management_agent_ollama.py:
# "num_predict": 400  # Reduce from 800
```

### Slow Performance
```bash
# Verify GPU acceleration is working
# In Python code, check num_gpu parameter:
"num_gpu": -1  # Should be -1 for all layers on GPU

# Monitor during inference
watch -n 0.5 nvidia-smi
# GPU Utilization should be 50-90%
```

---

## 📈 Recommended Testing Plan

### Day 1 (2 hours - $0.18 on Vast.ai)
1. Set up VM and install Ollama
2. Run basic demo with 3 test cases
3. Verify GPU acceleration working
4. Test improved prompts

### Day 2 (3 hours - $0.27)
1. Generate training data: `python generate_training_data.py`
2. Create fine-tuned model
3. Compare base vs fine-tuned accuracy
4. Document results

### Day 3 (2 hours - $0.18)
1. Stress test with 50+ requests
2. Benchmark performance
3. Collect production examples
4. Final evaluation

**Total cost**: ~$0.63 for comprehensive testing!

---

## 🎯 Summary

### Best Option for Your Use Case

**Just Testing (1-10 hours):**
→ **Vast.ai RTX 4000** @ $0.09/hr
- Cost for 10 hours: $0.90
- Perfect for quick validation

**Extended Testing (1-2 weeks):**
→ **RunPod RTX A4000** @ $0.19/hr
- More reliable than Vast.ai
- Better support
- Cost for 40 hours: $7.60

**Production Deployment:**
→ **GCP with L4 GPU** or **RunPod**
- Enterprise reliability
- Easy scaling
- Monitoring tools

### What You'll Learn
✅ GPU acceleration works (2-4x faster)
✅ Improved prompts increase accuracy (67-90%)
✅ Fine-tuning path is clear
✅ Total cost under $5 for full evaluation

### Next Steps
1. Sign up for Vast.ai
2. Add $10 credit
3. Launch RTX 4000 instance ($0.09/hr)
4. Follow setup steps above
5. Test your improved Ollama system!

---

## 📞 Support Links

- **Vast.ai**: https://vast.ai/docs/
- **RunPod**: https://docs.runpod.io/
- **GCP GPU Setup**: https://cloud.google.com/compute/docs/gpus
- **Ollama Docs**: https://ollama.com/docs
- **NVIDIA GPU Monitoring**: https://developer.nvidia.com/nvidia-system-management-interface
