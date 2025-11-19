# Banking Agent Demo with Semantic Routing

Virtual banking Agent demonstrates how semantic routing can intelligently route queries to the right tools based on the meaning of the user query without relying on expensive models which in turn saves token costs and reduces latency.

---

## Table of Contents

* [Demo Objectives](#demo-objectives)
* [Setup](#setup)
* [Running the Demo](#running-the-demo)
* [Slide Deck](#slide-deck)
* [Architecture](#architecture)
* [Known Issues](#known-issues)
* [Resources](#resources)
* [Maintainers](#maintainers)
* [License](#license)

---

## Demo Objectives

* Demonstrate semantic intent routing using RedisVL
* Showcase Redis message history for contextual chat
* Show agentic orchestration with LangGraph
* Illustrate tool execution using LangChain tools

---
## Setup

### Dependencies

- Python 3.11+
- Node.js 18+
- Docker (for Redis Stack)

### Configuration

1. Clone the repository:

```bash
git clone <repository-url>
cd banking-agent-semantic-routing-demo
```


2. Create a .env file in the project root:
   
```bash
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://localhost:6380
HISTORY_INDEX=bank:msg:index
HISTORY_NAMESPACE=bank:chat
HISTORY_TOPK_RECENT=8
HISTORY_TOPK_RELEVANT=6
HISTORY_DISTANCE_THRESHOLD=0.35
```
---
## Running the Demo

### Option 1: Docker Setup (Recommended)

```bash

# Start all services with Docker
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# RedisInsight: http://localhost:8001
```

### Option 2: Manual Setup

#### 1. Install Python Dependencies

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Start Redis Stack

```bash
# Option A: Docker (Recommended)
docker run -d --name redis-stack -p 6380:6379 -p 8001:8001 redis/redis-stack:latest

# Option B: Homebrew (macOS)
brew tap redis-stack/redis-stack
brew install redis-stack
redis-stack-server --daemonize yes
```

#### 3. Run the Backend

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start FastAPI server
python3 -m uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

#### 5. Run the Frontend

```bash
cd nextjs-app
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

## Architecture

- **Semantic Routing** (RedisVL): Routes queries to appropriate banking intents (loans, cards, FD, forex, etc.)
- **Slot-Filling Orchestration** (LangGraph): Manages conversation state and collects required information
- **Tool Execution** (LangChain): Executes banking operations (EMI calculation, card recommendations, etc.)
- **Modern Frontend** (Next.js 14 + TypeScript + Tailwind): Responsive banking UI with chat interface
- **Conversation Memory** (RedisVL MessageHistory): Structured conversation tracking

### Architecture Flow

```
User Query
    ↓
[Semantic Router] → Intent + Confidence + Required Slots
    ↓
[Parse Slots] → Extract values from text using LLM
    ↓
[Decide Next]
    ├→ Missing slots? → Ask follow-up question
    └→ All slots filled? → Call Tool
         ↓
    [Tool Execution] → Calculate/Recommend/Search
         ↓
    [Summarize] → Format response with bullets
         ↓
    Response to User
         ↓
    [Feedback System] → User rates helpfulness
         ↓
    [Memory Management] → Clear conversation if helpful
```

<img width="2158" height="2034" alt="image" src="https://github.com/user-attachments/assets/5689fa72-6a4e-44d4-aca2-7c75f8928a05" />

---

##  API Endpoints

### POST /chat

Intelligent chat endpoint with semantic routing and slot-filling.

**Request Body:**
```json
{
  "userId": "optional_user_id",
  "sessionId": "optional_session_id", 
  "text": "I need a loan",
  "meta": {}
}
```

**Response:**
```json
{
  "reply": "What loan amount are you looking for?",
  "pending": ["loan_amount", "tenure_months"],
  "router": {
    "intent": "loan",
    "confidence": "high",
    "score": 0.92
  },
  "proposal": null,
  "showFeedback": false,
  "model": "gpt-3.5-turbo"
}
```

### POST /chat/feedback

User feedback endpoint for conversation management.

**Request Body:**
```json
{
  "sessionId": "session_xyz",
  "helpful": true
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Thank you! Conversation cleared for a fresh start.",
  "cleared": true
}
```
---
## Example Conversations

### Loan EMI Calculation
```
User: I need a personal loan
Assistant: What loan amount are you looking for?
User: 5 lakhs for 3 years  
Assistant: Your EMI will be ₹16,134 per month for 36 months.
- Monthly EMI: ₹16,134
- Total Amount Payable: ₹5,80,832
- Total Interest: ₹80,832
- Principal: ₹5,00,000

Was this helpful? [ Yes] [ No]
```

### Credit Card Recommendation
```
User: I want a credit card
Assistant: What is your annual income?
User: 8 lakhs per year
Assistant: Based on your income of ₹8,00,000, we recommend the DemoBank Travel Elite.
- Annual Fee: ₹2,999
- 5X rewards on travel
- Airport lounge access
```
---

## Testing

### Test Router
```bash
python3 router_bank.py
```

### Test Orchestrator
```bash
python3 orchestrator.py
```

### Test API
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "I need a personal loan"}'
```

### Test System
```bash
python3 test_system.py
```
---

## Resources

* [RedisVL Semantic Routing User Guide](https://docs.redisvl.com/en/latest/user_guide/08_semantic_router.html)
* [RedisVL Semantic Routing API](https://docs.redisvl.com/en/latest/api/router.html)
* [Semantic Router Blog](https://medium.com/@bhavana0405/why-you-need-semantic-routing-in-your-langgraph-toolkit-a-beginners-guide-c09127bea209)


---

## Maintainers

* Bhavana Giri — [bhavanagiri](https://github.com/bhavana-giri)

---

## License

This project is licensed under the [MIT License](./LICENSE).

