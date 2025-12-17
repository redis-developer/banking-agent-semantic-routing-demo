"""
Semantic Router for Banking Application
Uses RedisVL to route user queries to appropriate banking intents
"""

import os
from typing import Dict, List, Optional
from redisvl.extensions.router import SemanticRouter, Route, RoutingConfig
from dotenv import load_dotenv

load_dotenv()

# Banking routes with example phrases
BANKING_ROUTES = [
    Route(
        name="credit_card",
        references=[
            "I want to apply for a credit card",
            "What credit cards do you offer?",
            "Tell me about your credit card benefits",
            "Which card is best for travel rewards?",
            "How do I get a new credit card?",
            "What's the credit limit on your cards?"
        ],
        metadata={
            "category": "cards",
            "required_slots": ["income", "card_type"],
            "handler": "cards_tool"
        },
        distance_threshold=0.4
    ),
    Route(
        name="loan",
        references=[
            "I need a personal loan",
            "How can I apply for a home loan?",
            "What's the interest rate on education loans?",
            "Tell me about car loan EMI",
            "I want to check loan eligibility",
            "How much loan can I get?"
        ],
        metadata={
            "category": "loans",
            "required_slots": ["loan_type", "amount", "tenure"],
            "handler": "loans_tool"
        },
        distance_threshold=0.4
    ),
    Route(
        name="savings_fd",
        references=[
            "What are the FD interest rates?",
            "I want to open a fixed deposit",
            "Tell me about savings account benefits",
            "How to create an FD ladder?",
            "What's the best investment option?",
            "Recurring deposit vs fixed deposit"
        ],
        metadata={
            "category": "savings",
            "required_slots": ["amount", "tenure"],
            "handler": "savings_tool"
        },
        distance_threshold=0.4
    ),
    Route(
        name="policy_faq",
        references=[
            "What are your branch timings?",
            "How do I reset my password?",
            "What documents do I need for KYC?",
            "Tell me about your privacy policy",
            "How to close my account?",
            "What are the service charges?"
        ],
        metadata={
            "category": "policy",
            "required_slots": [],
            "handler": "policy_rag_tool"
        },
        distance_threshold=0.45
    ),
    Route(
        name="forex_travel",
        references=[
            "I need foreign exchange for travel",
            "What's the USD to INR rate today?",
            "How to get forex card for abroad?",
            "Travel insurance options",
            "Best forex rates for Europe trip",
            "Currency exchange services"
        ],
        metadata={
            "category": "forex",
            "required_slots": ["currency", "amount"],
            "handler": "forex_tool"
        },
        distance_threshold=0.4
    ),
    Route(
        name="fraud_dispute",
        references=[
            "I see an unauthorized transaction",
            "My card was stolen",
            "Report a fraudulent charge",
            "Dispute a transaction",
            "Someone used my card without permission",
            "Block my credit card immediately"
        ],
        metadata={
            "category": "security",
            "required_slots": ["transaction_id", "description"],
            "handler": "fraud_tool"
        },
        distance_threshold=0.35
    )
]


class BankingRouter:
    """Semantic router for banking queries"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the banking semantic router
        
        Args:
            redis_url: Redis connection URL (defaults to env REDIS_URL)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        
        routing_config = RoutingConfig(
            max_k=3,  # Return top 3 matches
            aggregation_method="avg"
        )
        
        self.router = SemanticRouter(
            name="banking_router",
            routes=BANKING_ROUTES,
            routing_config=routing_config,
            redis_url=self.redis_url,
            overwrite=False  # Don't overwrite on each restart
        )
        
        print(f"Banking Router initialized with {len(BANKING_ROUTES)} routes")
    
    def route_text(self, text: str) -> Dict:
        """
        Route user text to appropriate banking intent
        
        Args:
            text: User query
            
        Returns:
            Dict with: {intent, score, confidence, metadata, topK}
        """
        matches = self.router(text)
        
        # Ensure matches is a list
        if not isinstance(matches, list):
            matches = [matches] if matches else []
        
        if not matches or matches[0].name is None:
            return {
                "intent": "unknown",
                "score": 0.0,
                "confidence": "none",
                "metadata": {},
                "topK": [],
                "threshold": None
            }
        
        top_match = matches[0]
        route = self.router.get(top_match.name)
        
        # Determine confidence level
        if top_match.distance < 0.2:
            confidence = "high"
        elif top_match.distance < 0.35:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "intent": top_match.name,
            "score": round(1 - top_match.distance, 3),  # Convert distance to similarity
            "distance": round(top_match.distance, 3),
            "confidence": confidence,
            "metadata": route.metadata if route else {},
            "topK": [
                {
                    "intent": m.name,
                    "score": round(1 - m.distance, 3),
                    "distance": round(m.distance, 3)
                }
                for m in matches if m.name is not None
            ],
            "threshold": route.distance_threshold if route else None
        }
    
    def get_required_slots(self, intent: str) -> List[str]:
        """Get required slots for an intent"""
        route = self.router.get(intent)
        if route and route.metadata:
            return route.metadata.get("required_slots", [])
        return []
    
    def get_handler(self, intent: str) -> Optional[str]:
        """Get handler name for an intent"""
        route = self.router.get(intent)
        if route and route.metadata:
            return route.metadata.get("handler")
        return None


# Singleton instance
_router_instance = None

def get_router() -> BankingRouter:
    """Get or create banking router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = BankingRouter()
    return _router_instance


if __name__ == "__main__":
    # Test the router
    router = BankingRouter()
    
    test_queries = [
        "I want to apply for a credit card",
        "What's the EMI for a 5 lakh home loan?",
        "Tell me about FD rates",
        "I need forex for my US trip",
        "Someone used my card without permission",
        "What are your branch timings?"
    ]
    
    print("\n" + "="*60)
    print("Testing Banking Semantic Router")
    print("="*60)
    
    for query in test_queries:
        result = router.route_text(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result['intent']} (score: {result['score']}, confidence: {result['confidence']})")
        print(f"Handler: {result['metadata'].get('handler', 'N/A')}")
        print(f"Required Slots: {result['metadata'].get('required_slots', [])}")

