"""
Savings & FD Tools - Fixed deposit ladder and investment suggestions
"""

from langchain_core.tools import tool
from typing import Dict, Any, List


# FD rates (tenure in months: rate %)
FD_RATES = {
    6: 6.5,
    12: 7.0,
    24: 7.25,
    36: 7.5,
    60: 7.75
}


@tool
def suggest_fd_ladder_tool(total_amount: float, tenure_months: int = 12) -> Dict[str, Any]:
    """
    Suggest FD ladder strategy for better liquidity and returns.
    
    Args:
        total_amount: Total amount to invest in INR
        tenure_months: Desired average tenure in months
        
    Returns:
        Dictionary with FD ladder strategy and projected returns
    """
    try:
        # Create ladder with multiple FDs
        ladder_strategy = []
        
        if tenure_months <= 12:
            # Short-term: Split into 3/6/12 months
            splits = [
                {"months": 6, "percentage": 0.3},
                {"months": 6, "percentage": 0.3},
                {"months": 12, "percentage": 0.4}
            ]
        else:
            # Long-term: Split into 12/24/36/60 months
            splits = [
                {"months": 12, "percentage": 0.25},
                {"months": 24, "percentage": 0.25},
                {"months": 36, "percentage": 0.25},
                {"months": 60, "percentage": 0.25}
            ]
        
        total_interest = 0
        total_maturity = 0
        
        for i, split in enumerate(splits, 1):
            months = split["months"]
            amount = total_amount * split["percentage"]
            rate = FD_RATES.get(months, 7.0)
            
            # Simple interest calculation
            interest = (amount * rate * months) / (12 * 100)
            maturity = amount + interest
            
            total_interest += interest
            total_maturity += maturity
            
            ladder_strategy.append({
                "fd_number": i,
                "amount": amount,
                "tenure": months,
                "rate": rate,
                "interest": interest,
                "maturity_amount": maturity
            })
        
        def format_inr(amount):
            return f"₹{amount:,.2f}"
        
        bullets = [
            f"Total Investment: {format_inr(total_amount)}",
            f"Total Interest Earned: {format_inr(total_interest)}",
            f"Total Maturity Value: {format_inr(total_maturity)}",
            f"Effective Return: {(total_interest/total_amount)*100:.2f}%",
            ""
        ]
        
        bullets.append("**FD Ladder Breakdown:**")
        for fd in ladder_strategy:
            bullets.append(
                f"FD-{fd['fd_number']}: {format_inr(fd['amount'])} @ {fd['rate']}% "
                f"for {fd['tenure']}m → Maturity: {format_inr(fd['maturity_amount'])}"
            )
        
        bullets.extend([
            "",
            "**Benefits of FD Ladder:**",
            "✓ Staggered maturity for regular liquidity",
            "✓ Balanced returns across tenures",
            "✓ Flexibility to reinvest at prevailing rates"
        ])
        
        return {
            "summary": f"Invest ₹{total_amount:,.0f} across {len(ladder_strategy)} FDs for optimal returns and liquidity.",
            "bullets": bullets,
            "data": {
                "total_investment": total_amount,
                "total_interest": round(total_interest, 2),
                "total_maturity": round(total_maturity, 2),
                "effective_rate": round((total_interest/total_amount)*100, 2),
                "ladder": ladder_strategy
            }
        }
    except Exception as e:
        return {
            "summary": f"Error creating FD ladder: {str(e)}",
            "bullets": ["Please check your input values and try again."],
            "data": {"error": str(e)}
        }

