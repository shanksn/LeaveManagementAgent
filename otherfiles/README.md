# Leave Management AI System

Two implementations of an AI-powered leave management system with policy evaluation and approval workflows.

---

## 📁 Project Structure

```
LlamaParsing/
├── gpt4_system/                      # GPT-4 based implementation (OpenAI API)
│   ├── leave_management_agent.py     # Main agent using GPT-4 Turbo
│   ├── leave_app_demo.py             # Demo application
│   ├── leave_app_demo_mock.py        # Mock version (no API needed)
│   └── test_gpt4_vs_ollama.py        # Comparison test script
│
├── ollama_system/                    # Ollama based implementation (Local LLM)
│   ├── leave_management_agent_ollama.py  # Main agent using Llama 3.2
│   ├── leave_app_demo_ollama.py      # Demo application
│   ├── test_improved_ollama.py       # Accuracy test script
│   └── generate_training_data.py     # Training data generator for fine-tuning
│
├── shared/                           # Shared resources
│   ├── hr_knowledge_base.json        # HR policies and approval hierarchy
│   └── .env                          # API keys (GPT-4 only)
│
├── docs/                             # Documentation
│   ├── GPT4_VS_OLLAMA_REPORT.md      # Accuracy comparison report
│   ├── CLOUD_GPU_DEPLOYMENT.md       # GPU server deployment guide
│   ├── SECURE_DEPLOYMENT.md          # Security best practices
│   ├── GPU_SERVER_LEARNING_GUIDE.md  # Learning experiments
│   ├── FINE_TUNING_GUIDE.md          # Fine-tuning instructions
│   └── ... (other documentation)
│
└── README.md                         # This file
```

---

## 🚀 Quick Start

### Option 1: GPT-4 System (Recommended for Production)

**Requirements:**
- OpenAI API key
- Python 3.8+
- `openai` and `python-dotenv` packages

**Setup:**
```bash
cd gpt4_system

# Install dependencies
pip install openai python-dotenv

# Ensure .env file exists in shared/ with:
# OPENAI_API_KEY=sk-proj-...

# Run demo
python3 leave_app_demo.py
```

**Features:**
- ✅ 100% accuracy on policy evaluation
- ✅ Comprehensive reasoning and recommendations
- ✅ Production-ready
- 💰 Cost: ~$0.01-0.02 per request

---

### Option 2: Ollama System (Free, Local)

**Requirements:**
- Ollama installed ([ollama.com](https://ollama.com))
- Llama 3.2 model
- Python 3.8+

**Setup:**
```bash
# Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:latest

cd ollama_system

# Run demo (no API key needed!)
python3 leave_app_demo_ollama.py
```

**Features:**
- ✅ Free (no API costs)
- ✅ Runs 100% locally
- ✅ GPU acceleration support
- ⚠️ ~67% accuracy (needs fine-tuning for production)

---

## 📊 Comparison: GPT-4 vs Ollama

| Feature | GPT-4 System | Ollama System |
|---------|--------------|---------------|
| **Accuracy** | 100% ✅ | ~67% ⚠️ |
| **Cost per Request** | $0.01-0.02 | $0.00 |
| **Speed** | 2-3 seconds | 1-2 seconds (with GPU) |
| **Privacy** | Data sent to OpenAI | 100% local |
| **Setup Complexity** | Easy (API key) | Medium (install Ollama) |
| **Production Ready** | ✅ Yes | ❌ No (needs fine-tuning) |
| **GPU Required** | ❌ No | ✅ Yes (for best performance) |

**See [docs/GPT4_VS_OLLAMA_REPORT.md](docs/GPT4_VS_OLLAMA_REPORT.md) for detailed comparison.**

---

## 🧪 Testing

### Test GPT-4 Accuracy
```bash
cd gpt4_system
python3 test_gpt4_vs_ollama.py
```

### Test Ollama Accuracy
```bash
cd ollama_system
python3 test_improved_ollama.py
```

### Run Mock Demo (No API)
```bash
cd gpt4_system
python3 leave_app_demo_mock.py
```

---

## 📚 HR Knowledge Base

Located in `shared/hr_knowledge_base.json`:

**Leave Policies:**
- Casual Leave: 12 days/year, max 3 consecutive
- Sick Leave: 12 days/year, max 5 consecutive
- Annual Leave: 21 days/year, max 15 consecutive
- Maternity Leave: 180 days
- Paternity Leave: 15 days
- Compensatory Leave: 24 days/year, max 2 consecutive

**Approval Hierarchy:**
- Manager: Level 2, approves up to 5 days
- Senior Manager: Level 3, approves up to 10 days
- HR: Level 4, approves up to 180 days

---

## 🔒 Security Notes

**IMPORTANT:** Never upload `.env` file to shared servers!

- ✅ **Safe:** Run GPT-4 system locally on your machine
- ✅ **Safe:** Run Ollama system on GPU server (no API keys)
- ❌ **UNSAFE:** Upload `.env` with API keys to shared cloud servers

See [docs/SECURE_DEPLOYMENT.md](docs/SECURE_DEPLOYMENT.md) for details.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [GPT4_VS_OLLAMA_REPORT.md](docs/GPT4_VS_OLLAMA_REPORT.md) | Accuracy comparison and recommendations |
| [CLOUD_GPU_DEPLOYMENT.md](docs/CLOUD_GPU_DEPLOYMENT.md) | Deploy to Vast.ai, RunPod, GCP ($0.09/hr) |
| [SECURE_DEPLOYMENT.md](docs/SECURE_DEPLOYMENT.md) | Security best practices for API keys |
| [GPU_SERVER_LEARNING_GUIDE.md](docs/GPU_SERVER_LEARNING_GUIDE.md) | Experiments for learning AI/ML |
| [FINE_TUNING_GUIDE.md](docs/FINE_TUNING_GUIDE.md) | Fine-tune Llama 3.2 for better accuracy |
| [IMPROVEMENTS_SUMMARY.md](docs/IMPROVEMENTS_SUMMARY.md) | Ollama optimization details |

---

## 🎯 Use Cases

### Production Deployment (Critical Accuracy)
→ Use **GPT-4 System** locally on your infrastructure
- 100% accuracy required for HR/legal compliance
- Cost: $10-20/year for 1000 requests
- No GPU needed

### Cost-Sensitive Deployment (After Fine-Tuning)
→ Use **Ollama System** on GPU server
- Fine-tune to 95%+ accuracy first (see [FINE_TUNING_GUIDE.md](docs/FINE_TUNING_GUIDE.md))
- Deploy on Vast.ai ($0.09/hr) or RunPod ($0.19/hr)
- 100% private, no external API calls

### Learning & Experimentation
→ Use **both** and compare
- Test different models with Ollama
- Benchmark GPU performance
- Learn fine-tuning and optimization
- See [GPU_SERVER_LEARNING_GUIDE.md](docs/GPU_SERVER_LEARNING_GUIDE.md)

---

## 🛠️ Example Usage

### GPT-4 System
```python
from leave_management_agent import LeaveManagementAgent

# Initialize agent
agent = LeaveManagementAgent()

# Create leave request
request = agent.create_leave_request(
    employee_name="John Doe",
    employee_id="EMP001",
    role="employee",
    leave_type="annual_leave",
    start_date="2025-12-20",
    end_date="2025-12-27",  # 8 days
    reason="Year-end vacation",
    current_balance=21
)

# View analysis
print(agent.generate_leave_report(request))

# Process approval
if request['status'] == 'pending_approval':
    approval = agent.process_approval(
        request_id=request['request_id'],
        approver_name="Manager Name",
        approver_role="manager",
        decision="approved",
        comments="Approved. Enjoy your vacation!"
    )
```

### Ollama System
```python
from leave_management_agent_ollama import LeaveManagementAgentOllama

# Initialize agent (Ollama must be running)
agent = LeaveManagementAgentOllama()

# Same API as GPT-4 version
request = agent.create_leave_request(...)
```

---

## 🚧 Known Limitations

### GPT-4 System:
- Requires internet connection
- Incurs API costs (~$0.01 per request)
- Data sent to OpenAI servers

### Ollama System:
- Current accuracy: ~67% (fails numerical comparisons)
- Requires fine-tuning for production use
- Needs GPU for good performance
- Larger models (8B+) more accurate but slower

---

## 🔮 Future Improvements

### For Ollama System:
1. ✅ Fine-tune on 500+ examples → 95%+ accuracy
2. ✅ Implement rule-based fallback for numerical checks
3. ✅ Test larger models (Llama 3.1 8B, Mistral 7B)
4. ✅ Add quantization optimization (4-bit, 8-bit)

### For Both Systems:
1. Add web UI (FastAPI + React)
2. Implement multi-tenant support
3. Add audit logging and compliance tracking
4. Integration with calendar systems
5. Email notifications for approvals

---

## 📊 Test Results Summary

**Test Case:** Annual leave, 8 days (max 15 allowed)

| System | Result | Reasoning |
|--------|--------|-----------|
| **GPT-4** | ✅ APPROVED | "Duration of 8 days does not exceed max of 15" |
| **Ollama (base)** | ❌ REJECTED | "Duration (8 days) > Max (15 days)" ← WRONG! |

**Conclusion:** GPT-4 is production-ready. Ollama needs fine-tuning.

---

## 💡 Tips

### Running Locally (Recommended)
```bash
# GPT-4 - run from your Mac (API key stays safe)
cd gpt4_system
python3 leave_app_demo.py

# Ollama - can run on GPU server (no secrets)
cd ollama_system
python3 leave_app_demo_ollama.py
```

### GPU Server Usage
- Upload only `ollama_system/` files (no .env!)
- Keep `gpt4_system/` and `shared/.env` on your local machine
- See [CLOUD_GPU_DEPLOYMENT.md](docs/CLOUD_GPU_DEPLOYMENT.md)

---

## 🤝 Contributing

Feel free to:
- Add more leave policies to `shared/hr_knowledge_base.json`
- Create additional test cases
- Fine-tune Ollama models and share results
- Add new features (web UI, integrations, etc.)

---

## 📄 License

This project is for educational and internal use.

---

## ❓ Questions?

See the `docs/` folder for detailed guides on:
- Deployment strategies
- Security best practices
- Fine-tuning instructions
- Learning experiments
- GPU server setup

---

**Built with:**
- OpenAI GPT-4 Turbo (API)
- Llama 3.2 via Ollama (local)
- Python 3.8+
- Love for automation and AI ❤️
