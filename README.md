# Banking AI Assistant - FastAPI + LangGraph + RedisVL + LangCache

An intelligent banking chatbot with semantic routing, slot-filling orchestration, and optional semantic caching. Built with FastAPI, LangGraph, RedisVL Semantic Router, LangChain tools, and Next.js frontend.

## 🏗️ Architecture

This application uses a modern AI stack:

- **Semantic Routing** (RedisVL): Routes queries to appropriate banking intents (loans, cards, FD, forex, etc.)
- **Slot-Filling Orchestration** (LangGraph): Manages conversation state and collects required information
- **Tool Execution** (LangChain): Executes banking operations (EMI calculation, card recommendations, etc.)
- **Optional Caching** (LangCache): Semantic caching for repeated queries (disabled by default)
- **Modern Frontend** (Next.js 14 + TypeScript + Tailwind): Responsive banking UI with chat interface

## 🚀 Quick Start

### 1. Install Python Dependencies

**Requires Python 3.11+**

```bash
# Using virtual environment (recommended)
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Redis Stack

**Required for semantic routing:**

```bash
# Option A: Docker (Recommended)
docker run -d --name redis-stack -p 6380:6379 -p 8001:8001 redis/redis-stack:latest

# Option B: Homebrew (macOS)
brew tap redis-stack/redis-stack
brew install redis-stack
redis-stack-server --daemonize yes
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6380

# LangCache (Optional - disabled by default)
USE_LANGCACHE=false
LANGCACHE_HOST=gcp-us-east4.langcache.redis.io
LANGCACHE_CACHE_ID=your_cache_id_here
LANGCACHE_API_KEY=your_langcache_api_key_here
```

### 4. Run the Backend

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start FastAPI server
python3 -m uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 5. Run the Frontend

```bash
cd nextjs-app
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📡 API Endpoints

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
  "model": "gpt-3.5-turbo"
}
```

**Action Types:**
- `ask`: System needs more information (follow-up question)
- `answer`: Final response with tool execution results

### GET /

Health check endpoint.

## 🎯 Supported Banking Intents

| Intent | Description | Required Slots | Tool |
|--------|-------------|----------------|------|
| **loan** | Personal/home/car/education loans | `loan_amount`, `tenure_months`, `interest_rate` | EMI Calculator |
| **credit_card** | Credit card applications | `income`, `card_type` | Card Recommender |
| **savings_fd** | Fixed deposits & savings | `amount`, `tenure` | FD Ladder Builder |
| **forex_travel** | Foreign exchange & travel | `currency`, `amount` | Forex Rates |
| **fraud_dispute** | Fraud reports & disputes | `transaction_id`, `description` | Fraud Handler |
| **policy_faq** | Policies & FAQs | - | Policy Search (RAG) |

## 💡 Example Conversations

### Loan EMI Calculation
```
User: I need a personal loan
Assistant: What loan amount are you looking for?
User: 5 lakhs for 3 years  
Assistant: Your EMI will be ₹16,134.24 per month...
```

### Credit Card Recommendation
```
User: I want a credit card
Assistant: What is your annual income?
User: 8 lakhs per year
Assistant: Based on your income of ₹8,00,000, we recommend the DemoBank Travel Elite...
```

## 🔧 LangCache (Optional)

**By default, LangCache is DISABLED**. To enable:

```bash
export USE_LANGCACHE=true
```

### How it works:
1. **Cache Check**: Semantic similarity search (threshold: 0.8)
2. **Cache Hit**: Return cached response (no LLM/tool call)
3. **Cache Miss**: Execute LangGraph flow, then cache final answer
4. **Benefits**: ⚡ Faster responses, 💰 Cost savings, 🔄 Semantic matching

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Web framework
- **LangGraph**: State machine orchestration  
- **LangChain**: Tool framework
- **RedisVL**: Semantic routing
- **Sentence Transformers**: Text embeddings
- **OpenAI**: LLM for slot extraction & summarization
- **LangCache**: Optional semantic caching

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Modern UI**: Glassmorphism design
