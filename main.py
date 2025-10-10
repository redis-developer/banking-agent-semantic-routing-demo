import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import openai
from dotenv import load_dotenv

# LangCache imports (preserved for future use)
try:
    from langcache import LangCache
    cache_available = True
except ImportError:
    cache_available = False
    print("⚠️  LangCache not available. Install with: pip install langcache")

# Feature flag for LangCache
USE_LANGCACHE = os.getenv("USE_LANGCACHE", "false").lower() == "true"

# Load environment variables
load_dotenv()

# Memory system imports (Redis-based)
try:
    from memory.history import add_message, get_context, clear_conversation
    memory_available = True
    print("✅ Redis-based conversation memory initialized")
except ImportError:
    memory_available = False
    print("⚠️  Memory system not available")
    # Fallback functions
    def add_message(session_id, role, text, intent="unknown", score=0.0):
        pass
    def get_context(session_id, limit=6):
        return None
    def clear_conversation(session_id):
        pass

# Initialize FastAPI app
app = FastAPI(title="Chat API", description="Simple chat API with OpenAI integration and caching")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize LangCache if available
lang_cache = None
if cache_available:
    try:
        # LangCache configuration (from working notebook)
        langcache_host = os.getenv('LANGCACHE_HOST', 'gcp-us-east4.langcache.redis.io')
        langcache_cache_id = os.getenv('LANGCACHE_CACHE_ID', '8cf48d66904b459094a84e2e8a9093c0')
        langcache_api_key = os.getenv('LANGCACHE_API_KEY')
        
        if langcache_api_key:
            lang_cache = LangCache(
                server_url=f"https://{langcache_host}",
                cache_id=langcache_cache_id,
                api_key=langcache_api_key
            )
            print("✅ LangCache initialized successfully")
        else:
            print("⚠️  LangCache API key not found in environment")
            cache_available = False
    except Exception as e:
        print(f"⚠️  Failed to initialize LangCache: {e}")
        cache_available = False

# Import orchestrator
try:
    from orchestrator import handle_turn
    orchestrator_available = True
except ImportError as e:
    orchestrator_available = False
    print(f"⚠️  Orchestrator not available: {e}")

# Pydantic models
class ChatRequest(BaseModel):
    userId: Optional[str] = None
    sessionId: Optional[str] = None
    text: str

class ChatResponse(BaseModel):
    reply: str
    userId: Optional[str] = None
    sessionId: Optional[str] = None
    pending: Optional[list] = None
    router: Optional[dict] = None
    proposal: Optional[dict] = None
    showFeedback: Optional[bool] = False  # Show "Was this helpful?" when true

@app.get("/")
async def root():
    return {"message": "Chat API is running! Use POST /chat to send messages."}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Banking AI Assistant API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Check if OpenAI API key is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        query = request.text.strip()
        session_id = request.sessionId or f"session_{request.userId or 'anon'}_{int(__import__('time').time())}"
        
        # Check cache first if available (only if USE_LANGCACHE is enabled)
        if USE_LANGCACHE and cache_available and lang_cache:
            try:
                cache_result = lang_cache.search(prompt=query, similarity_threshold=0.8)
                
                if cache_result.data:
                    # Cache hit - return cached response
                    cached_entry = cache_result.data[0]
                    print(f"🎯 CACHE HIT for query: '{query[:50]}...'")
                    return ChatResponse(
                        reply=cached_entry.response,
                        userId=request.userId,
                        sessionId=session_id
                    )
                else:
                    print(f"❌ CACHE MISS for query: '{query[:50]}...'")
            except Exception as e:
                print(f"⚠️  Cache lookup failed: {e}")
        
        # Use orchestrator if available, otherwise fallback to simple LLM
        if orchestrator_available:
            print(f"🤖 Using LangGraph Orchestrator for: '{query[:50]}...'")
            
            # Get conversation context from Redis (last 6 messages)
            context_text = get_context(session_id, limit=6)
            if context_text:
                print(f"💭 Retrieved conversation context for session {session_id}")
            
            # Call orchestrator with context
            result = handle_turn(
                user_id=request.userId,
                session_id=session_id,
                text=query,
                context=context_text
            )
            
            # Store this turn in Redis conversation context
            intent = result.get("router", {}).get("intent", "unknown")
            score = result.get("router", {}).get("score", 0.0)
            
            add_message(session_id, "user", query)
            add_message(session_id, "assistant", result['reply'], intent, score)
            print(f"💾 Stored conversation turn in Redis (session: {session_id})")
            
            # Store in cache if enabled
            if USE_LANGCACHE and cache_available and lang_cache:
                try:
                    lang_cache.set(prompt=query, response=result["reply"])
                    print(f"💾 Stored in cache: '{query[:50]}...'")
                except Exception as e:
                    print(f"⚠️  Failed to store in cache: {e}")
            
            # Show feedback when proposal is returned (task completed)
            show_feedback = bool(result.get("proposal"))
            
            return ChatResponse(
                reply=result["reply"],
                userId=request.userId,
                sessionId=session_id,
                pending=result.get("pending"),
                router=result.get("router"),
                proposal=result.get("proposal"),
                showFeedback=show_feedback
            )
        else:
            # Fallback to simple OpenAI call
            print(f"⚠️  Orchestrator unavailable, using fallback LLM")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful banking assistant. Provide concise, friendly responses to customer inquiries about banking services, account information, and general financial questions."
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content
            
            # Store in cache if enabled
            if USE_LANGCACHE and cache_available and lang_cache:
                try:
                    lang_cache.set(prompt=query, response=reply)
                    print(f"💾 Stored in cache: '{query[:50]}...'")
                except Exception as e:
                    print(f"⚠️  Failed to store in cache: {e}")
            
            return ChatResponse(
                reply=reply,
                userId=request.userId,
                sessionId=session_id
            )
        
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class FeedbackRequest(BaseModel):
    sessionId: str
    helpful: bool

@app.post("/chat/feedback")
async def chat_feedback(request: FeedbackRequest):
    """
    Handle user feedback. If helpful=true, clear the conversation to start fresh.
    
    Args:
        request: Feedback request with sessionId and helpful flag
        
    Returns:
        Success confirmation
    """
    if not request.sessionId or not request.sessionId.strip():
        raise HTTPException(status_code=400, detail="Missing sessionId")
    
    try:
        session_id = request.sessionId.strip()
        
        if request.helpful:
            # Clear Redis-based conversation context
            clear_conversation(session_id)
            print(f"✅ User feedback: helpful=true, cleared Redis context for session {session_id}")
            
            return {
                "ok": True,
                "message": "Thank you! Conversation cleared for a fresh start.",
                "cleared": True
            }
        else:
            print(f"📊 User feedback: helpful={request.helpful}, session {session_id}")
            return {
                "ok": True,
                "message": "Thank you for your feedback!",
                "cleared": False
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
