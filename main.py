import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import openai
from dotenv import load_dotenv

# LangCache imports
try:
    from langcache import LangCache
    cache_available = True
except ImportError:
    cache_available = False
    print("⚠️  LangCache not available. Install with: pip install langcache")

# Load environment variables
load_dotenv()

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

# Pydantic models
class ChatRequest(BaseModel):
    userId: Optional[str] = None
    text: str

class ChatResponse(BaseModel):
    reply: str
    userId: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Chat API is running! Use POST /chat to send messages."}

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
        reply = None
        
        # Check cache first if available
        if cache_available and lang_cache:
            try:
                cache_result = lang_cache.search(prompt=query, similarity_threshold=0.8)
                
                if cache_result.data:
                    # Cache hit - return cached response
                    cached_entry = cache_result.data[0]
                    reply = cached_entry.response
                    print(f"🎯 CACHE HIT for query: '{query[:50]}...'")
                else:
                    print(f"❌ CACHE MISS for query: '{query[:50]}...'")
            except Exception as e:
                print(f"⚠️  Cache lookup failed: {e}")
        
        # If no cached response, call OpenAI LLM
        if reply is None:
            print(f"🤖 Calling LLM for query: '{query[:50]}...'")
            
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
            
            # Extract the reply from OpenAI response
            reply = response.choices[0].message.content
            
            # Store in cache if available
            if cache_available and lang_cache:
                try:
                    lang_cache.set(prompt=query, response=reply)
                    print(f"💾 Stored in cache: '{query[:50]}...'")
                except Exception as e:
                    print(f"⚠️  Failed to store in cache: {e}")
        
        return ChatResponse(
            reply=reply,
            userId=request.userId
        )
        
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
