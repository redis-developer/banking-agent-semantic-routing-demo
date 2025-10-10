# Banking AI Assistant 🏦🤖

An intelligent banking chatbot with semantic routing, slot-filling orchestration, and optional semantic caching. Built with FastAPI, LangGraph, RedisVL Semantic Router, LangChain tools, and Next.js frontend.

## 🏗️ Architecture

This application uses a modern AI stack:

- **Semantic Routing** (RedisVL): Routes queries to appropriate banking intents (loans, cards, FD, forex, etc.)
- **Slot-Filling Orchestration** (LangGraph): Manages conversation state and collects required information
- **Tool Execution** (LangChain): Executes banking operations (EMI calculation, card recommendations, etc.)
- **Optional Caching** (LangCache): Semantic caching for repeated queries (disabled by default)
- **Modern Frontend** (Next.js 14 + TypeScript + Tailwind): Responsive banking UI with chat interface
- **Conversation Memory** (RedisVL MessageHistory): Structured conversation tracking with session management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for Redis Stack)

### Option 1: Docker Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd bank_langcache

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

#### 3. Configure Environment Variables

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

# RedisVL MessageHistory Configuration
HISTORY_INDEX=bank:msg:index
HISTORY_NAMESPACE=bank:chat
HISTORY_TOPK_RECENT=8
HISTORY_TOPK_RELEVANT=6
HISTORY_DISTANCE_THRESHOLD=0.35
```

#### 4. Run the Backend

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

### GET /health

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
Assistant: Your EMI will be ₹16,134 per month for 36 months.
- Monthly EMI: ₹16,134
- Total Amount Payable: ₹5,80,832
- Total Interest: ₹80,832
- Principal: ₹5,00,000

Was this helpful? [👍 Yes] [👎 No]
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

## 🐳 Docker Setup

The project includes Docker & Docker Compose for easy development and deployment.

### Quick Start with Docker

```bash
# Start all services (frontend, backend, redis)
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Services
- **frontend**: Next.js app (port 3000)
- **backend**: FastAPI app (port 8000) 
- **redis**: Redis Stack for semantic routing (port 6380)

### Features
- **Hot Reload**: Code changes are reflected immediately
- **Health Checks**: Services wait for dependencies to be healthy
- **Volume Mounts**: Source code is mounted for development
- **Environment Variables**: Loaded from `.env` file

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Rebuild services
docker-compose up --build

# Stop services
docker-compose down

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🧪 Testing

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

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Web framework
- **LangGraph**: State machine orchestration  
- **LangChain**: Tool framework
- **RedisVL**: Semantic routing & message history
- **Sentence Transformers**: Text embeddings
- **OpenAI**: LLM for slot extraction & summarization
- **LangCache**: Optional semantic caching

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Modern UI**: Glassmorphism design

### Infrastructure
- **Redis Stack**: Vector database & search
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration

## 🏗️ Architecture Flow

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

## 📊 Key Features

### Semantic Routing
- Intent recognition with confidence scores
- Routes work across different phrasings
- Example: "I need a loan" vs "loan application" vs "EMI calculator" all route to `loan`

### Slot-Filling
- Automatically extracts information from user messages
- Asks follow-up questions for missing slots
- Maintains conversation context across turns

### Tool Execution
- 6 specialized banking tools
- Returns structured data with summaries and bullet points
- Example EMI output includes: monthly payment, total interest, amortization details

### Conversation Memory
- Uses RedisVL MessageHistory for structured storage
- Session-based conversation tracking
- Automatic conversation clearing on positive feedback
- Rich metadata storage (intent, score, timestamps)

### Optional Caching
- LangCache preserved but disabled by default
- Enable with `export USE_LANGCACHE=true`
- Caches final answers to reduce LLM calls

## 🔄 User Feedback System

After completing a task (showing a proposal/recommendation), the system asks "Was this helpful?" with Yes/No buttons. When the user clicks **Yes**, the conversation memory is automatically cleared for a fresh start.

### Benefits
✅ **No stale data**: Old conversation context doesn't interfere with new requests  
✅ **User-controlled**: Clearing happens only when user confirms helpfulness  
✅ **Smooth UX**: Automatic "fresh start" without manual session management  
✅ **Feedback tracking**: Backend logs user satisfaction

## 🐛 Troubleshooting

### Redis Not Running?
```bash
docker ps | grep redis-stack
# If not running:
docker start redis-stack
```

### Python Version Wrong?
```bash
python3 --version  # Should be 3.11+
# If not, use: python3.11 or install from python.org
```

### Port Already in Use?
```bash
# Backend on different port:
uvicorn main:app --reload --port 8001

# Frontend on different port:
PORT=3001 npm run dev
```

### Import Errors?
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Docker Issues?
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Clean up Docker
docker-compose down -v
docker system prune -a
```

## 📁 Project Structure

```
bank_langcache/
├── main.py                    # FastAPI backend
├── orchestrator.py            # LangGraph state machine
├── router_bank.py             # Semantic router
├── test_system.py             # System tests
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker orchestration
├── Dockerfile.dev             # Backend Dockerfile
├── .env                       # Environment variables
├── memory/
│   ├── __init__.py
│   └── history.py             # RedisVL MessageHistory
├── tools/                     # LangChain banking tools
│   ├── __init__.py
│   ├── loans.py              # EMI calculator
│   ├── cards.py              # Card recommender
│   ├── savings.py            # FD ladder builder
│   ├── forex.py              # Forex rates
│   ├── fraud.py              # Fraud handler
│   └── policy_rag.py         # Policy search
└── nextjs-app/               # Next.js frontend
    ├── src/
    │   ├── app/
    │   └── components/
    │       └── ChatDock.tsx  # Main chat component
    ├── package.json
    └── Dockerfile.dev        # Frontend Dockerfile
```

## 🎉 Success Criteria Met

✅ Semantic routing with RedisVL  
✅ LangGraph orchestration  
✅ Slot-filling conversations  
✅ Tool execution with 6 banking tools  
✅ LangCache preserved (optional)  
✅ Modern frontend with intent display  
✅ Comprehensive documentation  
✅ Session management  
✅ Error handling & fallbacks  
✅ Docker containerization  
✅ User feedback system  
✅ Conversation memory management  

## 🚧 Next Steps (Optional Enhancements)

1. **Session Persistence**: Store conversation history in Redis
2. **Context Maintenance**: Pass full context across turns
3. **Tool Chaining**: Allow multiple tool calls in one turn
4. **Advanced RAG**: Real Redis vector search for policies
5. **User Authentication**: Integrate with user database
6. **Production LLM**: Use GPT-4 for better slot extraction
7. **Monitoring**: Add LangSmith tracing
8. **Testing**: Unit tests for tools and orchestrator

## 📚 Dependencies

### Python (Backend)
- fastapi: Web framework
- langgraph: State machine orchestration
- langchain: Tool framework
- langchain-openai: OpenAI integration
- redisvl: Semantic routing & message history
- sentence-transformers: Text embeddings
- langcache: Optional caching
- openai: LLM API

### Node.js (Frontend)
- next: 14.2.33
- react: 18
- typescript: 5
- tailwindcss: 3.4.1

### Infrastructure
- redis-stack: Vector database & search
- docker: Containerization

## 🎯 Result

A production-ready intelligent banking assistant that:
- Routes queries semantically
- Collects information through conversation
- Executes banking operations
- Returns structured, detailed responses
- Optionally caches for performance
- Displays beautifully in modern UI
- Manages conversation memory intelligently
- Provides user feedback system
- Runs in Docker containers

All while preserving the original LangCache functionality for future use! 🚀