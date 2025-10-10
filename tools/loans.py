"""
Loan Tools - EMI calculation and loan eligibility
"""

from langchain.tools import tool
from typing import Dict, Any


@tool
def calculate_emi_tool(loan_amount: float, interest_rate: float, tenure_months: int) -> Dict[str, Any]:
    """
    Calculate EMI (Equated Monthly Installment) for a loan.
    
    Args:
        loan_amount: Principal loan amount in INR
        interest_rate: Annual interest rate (e.g., 10.5 for 10.5%)
        tenure_months: Loan tenure in months
        
    Returns:
        Dictionary with EMI details, total payment, and interest
    """
    try:
        # Convert annual rate to monthly rate
        monthly_rate = (interest_rate / 12) / 100
        
        # EMI formula: P × r × (1 + r)^n / ((1 + r)^n - 1)
        if monthly_rate == 0:
            emi = loan_amount / tenure_months
        else:
            emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months) / \
                  (((1 + monthly_rate) ** tenure_months) - 1)
        
        total_payment = emi * tenure_months
        total_interest = total_payment - loan_amount
        
        # Format amounts in Indian numbering system (no decimal places)
        def format_inr(amount):
            return f"₹{round(amount):,}"
        
        return {
            "summary": f"Your EMI will be {format_inr(emi)} per month for {tenure_months} months.",
            "bullets": [
                f"Monthly EMI: {format_inr(emi)}",
                f"Total Amount Payable: {format_inr(total_payment)}",
                f"Total Interest: {format_inr(total_interest)}",
                f"Principal: {format_inr(loan_amount)}",
                f"Interest Rate: {interest_rate}% p.a.",
                f"Tenure: {tenure_months} months ({tenure_months//12} years {tenure_months%12} months)"
            ],
            "data": {
                "emi": round(emi, 2),
                "total_payment": round(total_payment, 2),
                "total_interest": round(total_interest, 2),
                "principal": loan_amount,
                "rate": interest_rate,
                "tenure": tenure_months
            }
        }
    except Exception as e:
        return {
            "summary": f"Error calculating EMI: {str(e)}",
            "bullets": ["Please check your input values and try again."],
            "data": {"error": str(e)}
        }

