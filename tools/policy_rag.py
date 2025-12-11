"""
Policy & FAQ Tools - RAG-based policy search
"""

from langchain_core.tools import tool
from typing import Dict, Any


# Mock policy database (in production, this would use Redis vector search)
POLICY_KB = {
    "branch timings": {
        "question": "What are your branch timings?",
        "answer": "Our branches are open Monday to Friday from 10:00 AM to 4:00 PM, and Saturday from 10:00 AM to 1:00 PM. We are closed on Sundays and public holidays."
    },
    "password reset": {
        "question": "How do I reset my password?",
        "answer": "To reset your password: 1) Visit the login page and click 'Forgot Password' 2) Enter your registered email/phone 3) Verify OTP 4) Set new password. Password must be 8-16 characters with at least one uppercase, one number, and one special character."
    },
    "kyc documents": {
        "question": "What documents do I need for KYC?",
        "answer": "For KYC verification, please provide: 1) Identity Proof (Aadhaar/PAN/Passport/Driving License) 2) Address Proof (Aadhaar/Utility Bill/Passport) 3) Recent photograph. All documents should be self-attested copies."
    },
    "account closure": {
        "question": "How to close my account?",
        "answer": "To close your account: 1) Visit your home branch 2) Submit account closure form with passbook/checkbook 3) Clear any pending dues 4) Balance will be transferred via check/NEFT. Processing takes 7-10 business days."
    },
    "service charges": {
        "question": "What are the service charges?",
        "answer": "Service charges vary by account type: Savings Account - ₹200/quarter if balance < minimum, ATM transactions - 5 free/month (₹20 thereafter), NEFT - Free, RTGS - ₹25-50 based on amount, Cheque book - ₹2/leaf."
    },
    "privacy policy": {
        "question": "Tell me about your privacy policy",
        "answer": "We protect your data with bank-grade encryption. We never share personal information with third parties without consent. Your data is used only for banking services. You can request data deletion anytime. Full policy at demobank.com/privacy"
    }
}


@tool
def search_policy_tool(query: str) -> Dict[str, Any]:
    """
    Search bank policies and FAQs using semantic matching.
    
    Args:
        query: User's policy/FAQ question
        
    Returns:
        Dictionary with policy answer and related information
    """
    try:
        # Simple keyword matching (in production, use Redis vector search)
        query_lower = query.lower()
        
        best_match = None
        best_score = 0
        
        for key, policy in POLICY_KB.items():
            # Simple keyword overlap score
            query_words = set(query_lower.split())
            policy_words = set(key.split() + policy["question"].lower().split())
            overlap = len(query_words & policy_words)
            
            if overlap > best_score:
                best_score = overlap
                best_match = policy
        
        if best_match:
            return {
                "summary": best_match["answer"],
                "bullets": [
                    f"**Question:** {best_match['question']}",
                    "",
                    "For more information:",
                    "📞 Customer Care: 1800-XXX-XXXX",
                    "🌐 Visit: demobank.com/help",
                    "💬 Chat with us on the app"
                ],
                "data": {
                    "matched_question": best_match["question"],
                    "confidence": "high" if best_score > 2 else "medium"
                }
            }
        else:
            return {
                "summary": "I couldn't find a specific policy answer. Let me connect you with customer support.",
                "bullets": [
                    "📞 Call: 1800-XXX-XXXX (24x7)",
                    "📧 Email: support@demobank.com",
                    "🌐 Help Center: demobank.com/help",
                    "💬 Visit nearest branch for detailed assistance"
                ],
                "data": {"matched": False}
            }
    except Exception as e:
        return {
            "summary": f"Error searching policies: {str(e)}",
            "bullets": ["Please contact customer support for assistance."],
            "data": {"error": str(e)}
        }

