"""
LangGraph Orchestrator for Banking Chat
Handles intent routing, slot filling, and tool execution
"""

import os
from typing import Dict, Any, List, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from router_bank import get_router
from tools import (
    calculate_emi_tool,
    recommend_card_tool,
    suggest_fd_ladder_tool,
    search_policy_tool,
    get_forex_rates_tool,
    handle_fraud_dispute_tool
)

load_dotenv()


# Define state schema
class ConversationState(TypedDict):
    session_id: str
    user_id: Optional[str]
    text: str
    intent: Optional[str]
    confidence: Optional[str]
    router_result: Optional[Dict]
    slots: Dict[str, Any]
    pending_slots: List[str]
    reply: str
    proposal: Optional[Dict]
    tool_result: Optional[Dict]
    history: List[Dict]


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


# Tool mapping
TOOL_MAP = {
    "loans_tool": calculate_emi_tool,
    "cards_tool": recommend_card_tool,
    "savings_tool": suggest_fd_ladder_tool,
    "policy_rag_tool": search_policy_tool,
    "forex_tool": get_forex_rates_tool,
    "fraud_tool": handle_fraud_dispute_tool
}


def route_intent_node(state: ConversationState) -> ConversationState:
    """Route user intent using semantic router with conversation context awareness"""
    
    # Check if we have conversation context with a recent intent
    reuse_intent = None
    reuse_metadata = None
    
    if state.get("history") and state["history"]:
        context = state["history"][0]
        # Check if there was a recent banking intent in last messages
        text_lower = state["text"].strip().lower()
        is_short_answer = len(state["text"].strip().split()) <= 3 or state["text"].strip().isdigit()
        
        # Common slot-answer patterns with full metadata
        if is_short_answer and ("loan" in context.lower() or "Intent: loan" in context):
            reuse_intent = "loan"
            reuse_metadata = {
                "required_slots": ["loan_type", "amount", "tenure"],
                "handler": "loans_tool"
            }
            print(f"💭 Reusing 'loan' intent from context (user answering slot question)")
        elif is_short_answer and ("credit" in context.lower() or "Intent: credit_card" in context):
            reuse_intent = "credit_card"
            reuse_metadata = {
                "required_slots": ["income", "card_type"],
                "handler": "cards_tool"
            }
            print(f"💭 Reusing 'credit_card' intent from context")
        elif is_short_answer and ("savings" in context.lower() or "fd" in context.lower() or "Intent: savings_fd" in context):
            reuse_intent = "savings_fd"
            reuse_metadata = {
                "required_slots": ["amount", "tenure"],
                "handler": "savings_tool"
            }
            print(f"💭 Reusing 'savings_fd' intent from context")
        elif is_short_answer and ("forex" in context.lower() or "currency" in context.lower() or "Intent: forex_travel" in context):
            reuse_intent = "forex_travel"
            reuse_metadata = {
                "required_slots": ["currency", "amount"],
                "handler": "forex_tool"
            }
            print(f"💭 Reusing 'forex_travel' intent from context")
        elif is_short_answer and ("policy" in context.lower() or "faq" in context.lower() or "Intent: policy_faq" in context):
            reuse_intent = "policy_faq"
            reuse_metadata = {
                "required_slots": [],
                "handler": "policy_rag_tool"
            }
            print(f"💭 Reusing 'policy_faq' intent from context")
        elif is_short_answer and ("fraud" in context.lower() or "dispute" in context.lower() or "Intent: fraud_dispute" in context):
            reuse_intent = "fraud_dispute"
            reuse_metadata = {
                "required_slots": ["transaction_id", "description"],
                "handler": "fraud_tool"
            }
            print(f"💭 Reusing 'fraud_dispute' intent from context")
    
    # If reusing intent from context, skip routing
    if reuse_intent:
        state["intent"] = reuse_intent
        state["confidence"] = "high"
        state["router_result"] = {
            "intent": reuse_intent,
            "confidence": "high",
            "score": 0.95,
            "source": "context",
            "metadata": reuse_metadata
        }
        state["pending_slots"] = reuse_metadata.get("required_slots", [])
    else:
        # Normal routing for new queries
        router = get_router()
        result = router.route_text(state["text"])
        
        state["intent"] = result["intent"]
        state["confidence"] = result["confidence"]
        state["router_result"] = result
        
        # Get required slots for this intent
        if result["intent"] != "unknown":
            required_slots = result["metadata"].get("required_slots", [])
            state["pending_slots"] = required_slots.copy()
        else:
            state["pending_slots"] = []
        
        print(f"Routed to: {result['intent']} (confidence: {result['confidence']}, score: {result['score']})")
    
    return state


def parse_slots_node(state: ConversationState) -> ConversationState:
    """Extract slot values from user text using LLM with conversation context"""
    if not state["pending_slots"]:
        return state
    
    # Build context from history
    conversation_context = ""
    if state.get("history") and state["history"]:
        conversation_context = "\n\nPrevious conversation:\n" + state["history"][0]
    
    # Use LLM to extract slot values with context
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a slot extractor for a banking chatbot.
Extract the following information from the CURRENT USER MESSAGE ONLY:
{slots_needed}

CRITICAL RULES:
1. ONLY extract values from the user's current message, NOT from the assistant's questions.
2. Extract example values that the assistant mentioned (like "USD/EUR/GBP" from the question).
3. If the assistant asked "Which currency? (USD/EUR/GBP)" and user said "i want forex card", return null for currency.
4. Only extract if the user EXPLICITLY provided the information in their current message.
5. Use EXACT slot names from the list above.

Return ONLY a JSON object with extracted values. Use null if NOT found in current user message.
Examples:
- Slots: currency, amount
  User: "I need USD for my trip" → {{"currency": "USD", "amount": null}}
- Slots: currency, amount  
  Assistant asked: "Which currency? (USD/EUR/GBP)"
  User: "EUR" → {{"currency": "EUR", "amount": null}}
- Slots: currency, amount
  Assistant asked: "Which currency?"
  User: "i want forex card" → {{"currency": null, "amount": null}}  (user didn't answer)
- Slots: loan_type
  User: "personal loan" → {{"loan_type": "personal"}}
{context}"""),
        ("human", "{text}")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({
            "slots_needed": ", ".join(state["pending_slots"]),
            "text": state["text"],
            "context": conversation_context
        })
        
        # Parse LLM response (expecting JSON)
        import json
        extracted = json.loads(response.content)
        
        # Update slots directly
        for slot, value in extracted.items():
            if value is not None:
                state["slots"][slot] = value
                if slot in state["pending_slots"]:
                    state["pending_slots"].remove(slot)
        
        print(f"Extracted slots: {extracted}")
        print(f"Pending slots: {state['pending_slots']}")
        
    except Exception as e:
        print(f"Slot extraction failed: {e}")
    
    return state


def decide_next_node(state: ConversationState) -> ConversationState:
    """Decide whether to ask for more info or call tool"""
    if state["intent"] == "unknown":
        state["reply"] = "I'm not sure I understand. Could you please rephrase? I can help with loans, credit cards, FD investments, forex, policies, and fraud reports."
        return state
    
    # Remove already-filled slots from pending_slots
    filled_slots = set(state["slots"].keys())
    state["pending_slots"] = [s for s in state["pending_slots"] if s not in filled_slots]
    
    print(f"Filled slots: {list(filled_slots)}")
    print(f"Still pending: {state['pending_slots']}")
    
    if state["pending_slots"]:
        # Need more information
        next_slot = state["pending_slots"][0]
        
        # Generate question for the slot
        slot_questions = {
            "loan_amount": "What loan amount are you looking for?",
            "loan_type": "What type of loan do you need? (personal/home/car/education)",
            "interest_rate": "What interest rate were you quoted? (if you know)",
            "income": "What is your annual income?",
            "card_type": "What type of benefits are you interested in? (travel/cashback/premium)",
            "amount": "What amount are you planning to invest/need?",
            "tenure": "For how long? (in months)",
            "currency": "Which currency do you need? (USD/EUR/GBP/etc.)",
            "transaction_id": "What is the transaction ID? (or say 'immediate' to block card now)",
            "description": "Please describe the issue in detail."
        }
        
        state["reply"] = slot_questions.get(next_slot, f"Could you provide: {next_slot}?")
    else:
        # All slots filled, ready to call tool
        pass
    
    return state


def call_tool_node(state: ConversationState) -> ConversationState:
    """Execute the appropriate tool with collected slots"""
    handler_name = state["router_result"]["metadata"].get("handler")
    
    if not handler_name or handler_name not in TOOL_MAP:
        state["reply"] = "I found your intent but couldn't process it. Please contact support."
        return state
    
    tool = TOOL_MAP[handler_name]
    
    try:
        # Map slots to tool parameters
        tool_params = {}
        
        # Tool-specific parameter mapping
        if handler_name == "loans_tool":
            tool_params = {
                "loan_amount": state["slots"].get("amount", 500000),
                "interest_rate": state["slots"].get("interest_rate", 10.5),
                "tenure_months": state["slots"].get("tenure", 60)
            }
        elif handler_name == "cards_tool":
            tool_params = {
                "income": state["slots"].get("income", 500000),
                "preferred_benefits": state["slots"].get("card_type", "general")
            }
        elif handler_name == "savings_tool":
            tool_params = {
                "total_amount": state["slots"].get("amount", 100000),
                "tenure_months": state["slots"].get("tenure", 12)
            }
        elif handler_name == "forex_tool":
            tool_params = {
                "currency": state["slots"].get("currency", "USD"),
                "amount": state["slots"].get("amount", 50000)
            }
        elif handler_name == "fraud_tool":
            tool_params = {
                "transaction_id": state["slots"].get("transaction_id", "immediate"),
                "description": state["text"]
            }
        elif handler_name == "policy_rag_tool":
            tool_params = {
                "query": state["text"]
            }
        
        print(f"🔧 Calling {handler_name} with params: {tool_params}")
        result = tool.invoke(tool_params)
        
        state["tool_result"] = result
        
    except Exception as e:
        print(f"Tool execution failed: {e}")
        state["tool_result"] = {
            "summary": f"Sorry, I encountered an error: {str(e)}",
            "bullets": ["Please try again or contact support."],
            "data": {"error": str(e)}
        }
    
    return state


def summarize_node(state: ConversationState) -> ConversationState:
    """Generate final response summary"""
    if state["tool_result"]:
        # Format tool result into response
        result = state["tool_result"]
        state["reply"] = result.get("summary", "Here's what I found:")
        state["proposal"] = {
            "bullets": result.get("bullets", []),
            "data": result.get("data", {})
        }
    
    return state


def should_continue(state: ConversationState) -> str:
    """Determine next node in the graph"""
    # If we have pending slots, we're asking for more info - end here
    if state["pending_slots"]:
        return END
    # If we have a tool result, we need to summarize it
    elif state.get("tool_result"):
        return "summarize"
    # If we have slots but no tool result, we need to call the tool
    elif state["slots"] and state["router_result"]:
        return "call_tool"
    # Otherwise, we're done
    else:
        return END


# Build the graph
def build_graph() -> StateGraph:
    """Construct the LangGraph state machine"""
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("route_intent", route_intent_node)
    workflow.add_node("parse_slots", parse_slots_node)
    workflow.add_node("decide_next", decide_next_node)
    workflow.add_node("call_tool", call_tool_node)
    workflow.add_node("summarize", summarize_node)
    
    # Define edges
    workflow.set_entry_point("route_intent")
    workflow.add_edge("route_intent", "parse_slots")
    workflow.add_edge("parse_slots", "decide_next")
    workflow.add_conditional_edges(
        "decide_next",
        should_continue,
        {
            "call_tool": "call_tool",
            "summarize": "summarize",
            END: END
        }
    )
    workflow.add_edge("call_tool", "summarize")
    workflow.add_edge("summarize", END)
    
    return workflow.compile()


# Global graph instance
_graph = None

def get_graph():
    """Get or create graph instance"""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def extract_slots_from_context(context: str) -> Dict[str, Any]:
    """Extract previously filled slots from conversation context"""
    slots = {}
    
    # Parse context for common slot patterns
    import re
    
    # Amount patterns - look for numbers >= 10000
    amount_matches = re.findall(r'\b(\d{5,})\b', context)
    if amount_matches:
        # Take the first large number as amount
        slots["amount"] = int(amount_matches[0])
    
    # Loan type patterns
    loan_type_match = re.search(r'\b(personal|home|car|education)(?:\s+loan)?\b', context, re.IGNORECASE)
    if loan_type_match:
        slots["loan_type"] = loan_type_match.group(1).lower()
    
    # Tenure patterns - look for "X months" or "X years" OR small numbers (2-60) near tenure-related words
    tenure_match = re.search(r'(?:tenure|duration|period|months?|years?).*?(\d+)\s*(months?|years?)?', context, re.IGNORECASE)
    if not tenure_match:
        # Also try: user just said a number after "how long"
        tenure_match = re.search(r'(?:how long|tenure).*?(\d+)', context, re.IGNORECASE)
    if tenure_match:
        num = int(tenure_match.group(1))
        unit = tenure_match.group(2).lower() if tenure_match.lastindex >= 2 and tenure_match.group(2) else ''
        # If unit is specified
        if 'year' in unit:
            slots["tenure"] = num * 12
        elif 'month' in unit or (2 <= num <= 360):  # reasonable tenure range
            slots["tenure"] = num
    
    # Card type patterns
    if re.search(r'\b(travel|cashback|premium|rewards?)\b', context, re.IGNORECASE):
        match = re.search(r'\b(travel|cashback|premium|rewards?)\b', context, re.IGNORECASE)
        if match:
            slots["card_type"] = match.group(1).lower()
    
    # Income patterns
    income_match = re.search(r'income.*?(\d{5,})', context, re.IGNORECASE)
    if income_match:
        slots["income"] = int(income_match.group(1))
    
    return slots


def handle_turn(
    user_id: Optional[str],
    session_id: str,
    text: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle a single conversation turn
    
    Args:
        user_id: Optional user identifier
        session_id: Session identifier
        text: User's message
        context: Optional conversation context from memory
        
    Returns:
        Response dict with reply, slots, etc.
    """
    # Extract previously filled slots from context
    # TODO: Store slots locally in a dict and check performance
    existing_slots = extract_slots_from_context(context) if context else {}
    
    # Initialize state with optional context and existing slots
    initial_state: ConversationState = {
        "session_id": session_id,
        "user_id": user_id,
        "text": text,
        "intent": None,
        "confidence": None,
        "router_result": None,
        "slots": existing_slots,  # Preserve slots from previous turns
        "pending_slots": [],
        "reply": "",
        "proposal": None,
        "tool_result": None,
        "history": [context] if context else []
    }
    
    # Run the graph
    graph = get_graph()
    final_state = graph.invoke(initial_state)
    
    # Format response
    return {
        "reply": final_state["reply"],
        "pending": final_state.get("pending_slots", []),
        "router": {
            "intent": final_state.get("intent"),
            "confidence": final_state.get("confidence"),
            "score": final_state["router_result"].get("score") if final_state.get("router_result") else None
        },
        "proposal": final_state.get("proposal")
    }


if __name__ == "__main__":
    # Test the orchestrator
    print("\n" + "="*60)
    print("Testing LangGraph Orchestrator")
    print("="*60)
    
    test_cases = [
        "I want to apply for a personal loan",
        "My income is 8 lakhs per year",
        "I need 10 lakhs for 5 years"
    ]
    
    session_id = "test_session_123"
    
    for text in test_cases:
        print(f"\n{'='*60}")
        print(f"User: {text}")
        print(f"{'='*60}")
        
        response = handle_turn(
            user_id="test_user",
            session_id=session_id,
            text=text
        )
        
        print(f"\nAssistant: {response['reply']}")
        if response.get('proposal'):
            print(f"\nDetails:")
            for bullet in response['proposal'].get('bullets', [])[:5]:
                print(f"  • {bullet}")
        print(f"\nRouter: {response['router']}")

