#  LLM Observability Dashboard

A real-time monitoring and analytics system for Large Language Model (LLM) applications.  
It records and visualizes latency, token usage, errors, model performance, and system alerts — enabling full production-grade observability.

##  Key Features
| Module | Description |
|--------|-------------|
| 🔹 Real-time Logging | Stores every LLM request + response with cost & latency |
| 🔹 Analytics Dashboard | Visual trend insights for latency, tokens & errors |
| 🔹 Alert Engine | High-latency, cost spike & error-rate detection |
| 🔹 Multi-Model Support | Auto-detects best available GROQ model |
| 🔹 Cost Tracking | `cost_usd` and `cost_inr` stored for each call |
| 🔹 Daily Metrics | Aggregates performance on a per-day basis |

## 📁 Folder Structure
LLM-Observability-Dashboard/
│ main.py
│ .env (store your API Key Hear)
│ llm_logs.db (auto-created)
│
├─ core/
│ ├─ db.py
│ ├─ logger.py
│ ├─ analytics.py
│ ├─ currency.py
│ ├─ alerts.py
│ └─ init.py
│
├─ dashboard/
│ ├─ app.py
│ └─ pages/
│ ├─ Analytics.py
│ ├─ Alerts.py
│ ├─ Models.py
│ ├─ Prompts.py
│ ├─ Errors.py
│ └─ Logs.py
│
├─ assets/
│ └─ screenshots (optional)
│
└─ requirements.txt

## Setup Instructions

### Clone the Repository
```bash
git clone https://github.com/BadgujarHarshal/LLM-Observability-Dashboard.git
cd LLM-Observability-Dashboard

### WROKING PROCESS

1st pip install -r requirements.txt

2nd Create .env file:
"
GROQ_API_KEY=your_api_key
"
3rd Run LLM Interaction Script
     python main.py

4th Start Dashboard
    streamlit run dashboard/app.py
