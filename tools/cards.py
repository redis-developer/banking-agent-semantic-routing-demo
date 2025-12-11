"""
Credit Card Tools - Card recommendations and benefits
"""

from langchain_core.tools import tool
from typing import Dict, Any, List


# Card database
CREDIT_CARDS = {
    "travel": {
        "name": "DemoBank Travel Elite",
        "benefits": ["5X rewards on travel", "Airport lounge access", "Complimentary travel insurance"],
        "annual_fee": 2999,
        "min_income": 500000,
        "reward_rate": 5
    },
    "cashback": {
        "name": "DemoBank Cashback Plus",
        "benefits": ["5% cashback on online shopping", "2% on dining", "Fuel surcharge waiver"],
        "annual_fee": 999,
        "min_income": 300000,
        "reward_rate": 5
    },
    "premium": {
        "name": "DemoBank Platinum Reserve",
        "benefits": ["10X rewards", "Concierge service", "Golf privileges", "Priority customer care"],
        "annual_fee": 10000,
        "min_income": 1500000,
        "reward_rate": 10
    },
    "entry": {
        "name": "DemoBank Silver Card",
        "benefits": ["1% rewards", "EMI conversion", "Online fraud protection"],
        "annual_fee": 0,
        "min_income": 200000,
        "reward_rate": 1
    }
}


@tool
def recommend_card_tool(income: float, preferred_benefits: str = "general") -> Dict[str, Any]:
    """
    Recommend credit cards based on income and preferred benefits.
    
    Args:
        income: Annual income in INR
        preferred_benefits: Type of benefits (travel, cashback, premium, general)
        
    Returns:
        Dictionary with card recommendations
    """
    try:
        # Normalize benefit type
        benefit_type = preferred_benefits.lower()
        if benefit_type not in ["travel", "cashback", "premium", "general"]:
            benefit_type = "general"
        
        eligible_cards = []
        
        # Check eligibility for each card
        for card_type, card_info in CREDIT_CARDS.items():
            if income >= card_info["min_income"]:
                eligible_cards.append({
                    "type": card_type,
                    **card_info
                })
        
        if not eligible_cards:
            return {
                "summary": "Based on your income, we recommend building your credit profile first.",
                "bullets": [
                    "Consider a secured credit card to start",
                    "Minimum income required: ₹2,00,000 per annum",
                    "You can reapply once your income increases"
                ],
                "data": {"eligible": False, "cards": []}
            }
        
        # Sort by reward rate (descending)
        eligible_cards.sort(key=lambda x: x["reward_rate"], reverse=True)
        
        # Pick best match based on preference
        if benefit_type != "general" and benefit_type in CREDIT_CARDS:
            if income >= CREDIT_CARDS[benefit_type]["min_income"]:
                recommended = CREDIT_CARDS[benefit_type]
                card_type = benefit_type
            else:
                recommended = eligible_cards[0]
                card_type = eligible_cards[0]["type"]
        else:
            recommended = eligible_cards[0]
            card_type = eligible_cards[0]["type"]
        
        bullets = [
            f"💳 Recommended: **{recommended['name']}**",
            f"Annual Fee: ₹{recommended['annual_fee']:,}",
            f"Reward Rate: {recommended['reward_rate']}X points"
        ]
        bullets.extend([f"✓ {benefit}" for benefit in recommended["benefits"]])
        
        return {
            "summary": f"Based on your income of ₹{income:,.0f}, we recommend the {recommended['name']}.",
            "bullets": bullets,
            "data": {
                "recommended_card": card_type,
                "card_details": recommended,
                "all_eligible": [
                    {
                        "type": c["type"],
                        "name": c["name"],
                        "annual_fee": c["annual_fee"]
                    }
                    for c in eligible_cards
                ]
            }
        }
    except Exception as e:
        return {
            "summary": f"Error recommending card: {str(e)}",
            "bullets": ["Please try again with valid income information."],
            "data": {"error": str(e)}
        }

