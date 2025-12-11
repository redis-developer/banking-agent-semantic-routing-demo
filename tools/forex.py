"""
Forex & Travel Tools - Currency exchange and travel services
"""

from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime


# Mock forex rates (in production, fetch from live API)
FOREX_RATES = {
    "USD": 83.25,
    "EUR": 90.50,
    "GBP": 105.75,
    "AED": 22.65,
    "SGD": 62.40,
    "AUD": 54.30,
    "CAD": 61.20,
    "CHF": 94.80
}


@tool
def get_forex_rates_tool(currency: str, amount: float = 1000.0) -> Dict[str, Any]:
    """
    Get forex rates and travel currency information.
    
    Args:
        currency: Currency code (USD, EUR, GBP, etc.)
        amount: Amount in INR to convert
        
    Returns:
        Dictionary with forex rates and travel recommendations
    """
    try:
        currency = currency.upper()
        
        if currency not in FOREX_RATES:
            available = ", ".join(FOREX_RATES.keys())
            return {
                "summary": f"Currency {currency} not available. We support: {available}",
                "bullets": [f"Available currencies: {available}"],
                "data": {"error": "unsupported_currency"}
            }
        
        rate = FOREX_RATES[currency]
        foreign_amount = amount / rate
        
        # Calculate with markup (2%)
        card_rate = rate * 1.02
        card_amount = amount / card_rate
        
        def format_inr(amt):
            return f"₹{amt:,.2f}"
        
        bullets = [
            f"**Today's Rate (Cash):** 1 {currency} = ₹{rate:.2f}",
            f"{format_inr(amount)} = {foreign_amount:,.2f} {currency}",
            "",
            f"**Forex Card Rate:** 1 {currency} = ₹{card_rate:.2f}",
            f"{format_inr(amount)} = {card_amount:,.2f} {currency}",
            "",
            "**Services Available:**",
            "💳 Multi-currency forex card",
            "💵 Foreign currency cash",
            "🛡️ Travel insurance",
            "✈️ Airport lounge access",
            "",
            "**Documents Required:**",
            "• Valid passport",
            "• Visa (if applicable)",
            "• Travel tickets",
            "• PAN card",
            "",
            "📍 Visit any branch or order online"
        ]
        
        return {
            "summary": f"For ₹{amount:,.0f}, you'll get approximately {foreign_amount:,.2f} {currency} "
                      f"at today's rate of ₹{rate:.2f} per {currency}.",
            "bullets": bullets,
            "data": {
                "currency": currency,
                "inr_amount": amount,
                "foreign_amount": round(foreign_amount, 2),
                "exchange_rate": rate,
                "card_rate": round(card_rate, 2),
                "card_amount": round(card_amount, 2),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        }
    except Exception as e:
        return {
            "summary": f"Error fetching forex rates: {str(e)}",
            "bullets": ["Please contact our forex desk for current rates."],
            "data": {"error": str(e)}
        }

