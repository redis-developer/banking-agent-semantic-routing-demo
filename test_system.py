"""
Quick system test script
Tests router, orchestrator, and API integration
"""

import requests
import json

# Test configuration
API_URL = "http://localhost:8000"
SESSION_ID = "test_session_" + str(__import__('time').time())

def test_health():
    """Test API health endpoint"""
    print("\n" + "="*60)
    print("Test 1: API Health Check")
    print("="*60)
    
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_chat_endpoint(query, description):
    """Test chat endpoint with a query"""
    print("\n" + "="*60)
    print(f"Test: {description}")
    print("="*60)
    print(f"Query: {query}")
    
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "text": query,
            "sessionId": SESSION_ID,
            "userId": "test_user"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nBot Reply: {data.get('reply')}")
        print(f"Action: {data.get('action')}")
        print(f"Intent: {data.get('router', {}).get('intent')}")
        print(f"Confidence: {data.get('router', {}).get('confidence')}")
        print(f"Score: {data.get('router', {}).get('score')}")
        
        
        if data.get('proposal'):
            bullets = data['proposal'].get('bullets', [])
            if bullets:
                print(f"\nDetails (first 3):")
                for bullet in bullets[:3]:
                    print(f"  • {bullet}")
        
        print("✅ Test passed")
        return data
    else:
        print(f"❌ Test failed: {response.text}")
        return None

def main():
    print("\n" + "="*60)
    print("Banking AI Assistant - System Test")
    print("="*60)
    print(f"API: {API_URL}")
    print(f"Session ID: {SESSION_ID}")
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Loan query
        test_chat_endpoint(
            "I need a personal loan of 5 lakhs for 3 years",
            "Loan Query (with slots)"
        )
        
        # Test 3: Credit card query
        test_chat_endpoint(
            "I want a credit card",
            "Credit Card Query (missing slots)"
        )
        
        # Test 4: FD query
        test_chat_endpoint(
            "Tell me about fixed deposit rates for 2 lakhs",
            "FD Query"
        )
        
        # Test 5: Forex query
        test_chat_endpoint(
            "I need USD 1000 for my US trip",
            "Forex Query"
        )
        
        # Test 6: Fraud query
        test_chat_endpoint(
            "Someone used my card without permission, transaction ID TXN123456",
            "Fraud Query"
        )
        
        # Test 7: Policy query
        test_chat_endpoint(
            "What are your branch timings?",
            "Policy Query"
        )
        
        print("\n" + "="*60)
        print("All Tests Completed! ✅")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API")
        print("Make sure the backend is running: uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

