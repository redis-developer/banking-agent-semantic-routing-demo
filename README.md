# Semantic Routing with Redis: A Banking Chatbot

A banking chatbot with semantic routing and slot-filling orchestration. Built with FastAPI, LangGraph, RedisVL Semantic Router, LangChain tools, and Next.js frontend.

## Architecture

- **Semantic Routing** (RedisVL): Routes queries to appropriate banking intents (loans, cards, FD, forex, etc.)
- **Slot-Filling Orchestration** (LangGraph): Manages conversation state and collects required information
- **Tool Execution** (LangChain): Executes banking operations (EMI calculation, card recommendations, etc.)
- **Modern Frontend** (Next.js 14 + TypeScript + Tailwind): Responsive banking UI with chat interface
- **Conversation Memory** (RedisVL MessageHistory): Structured conversation tracking

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for Redis Stack)

### Option 1: Docker Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd bank_semantic_router

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


## Docker Setup

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

## Tech Stack

### Backend
- **FastAPI**: Web framework
- **LangGraph**: State machine orchestration  
- **LangChain**: Tool framework
- **RedisVL**: Semantic routing & message history
- **Sentence Transformers**: Text embeddings
- **OpenAI**: LLM for slot extraction & summarization

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Modern UI**: Glassmorphism design

### Infrastructure
- **Redis Stack**: Vector database & search
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration

## Architecture Flow

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
<img width="2158" height="2034" alt="image" src="https://github.com/user-attachments/assets/a6cf4d14-2939-4818-9ad8-8c01b749549d" />


## Key Features

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


## Troubleshooting

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

## Dependencies

### Python (Backend)
- fastapi: Web framework
- langgraph: State machine orchestration
- langchain: Tool framework
- langchain-openai: OpenAI integration
- redisvl: Semantic routing & message history
- sentence-transformers: Text embeddings
- openai: LLM API

### Node.js (Frontend)
- next: 14.2.33
- react: 18
- typescript: 5
- tailwindcss: 3.4.1

### Infrastructure
- redis-stack: Vector database & search
- docker: Containerization

## Result

A production-ready banking assistant that:
- Routes queries semantically
- Collects information through conversation
- Executes banking operations
- Returns structured, detailed responses
- Displays beautifully in modern UI
- Manages conversation memory intelligently
- Provides user feedback system
- Runs in Docker containers

A complete semantic routing solution for intelligent banking conversations!
