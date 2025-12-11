"""
Fraud & Dispute Tools - Handle security issues and disputes
"""

from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime
import random


@tool
def handle_fraud_dispute_tool(transaction_id: str, description: str) -> Dict[str, Any]:
    """
    Handle fraud reports and transaction disputes.
    
    Args:
        transaction_id: Transaction ID or "immediate" for card blocking
        description: Description of the fraud/dispute
        
    Returns:
        Dictionary with dispute case details and next steps
    """
    try:
        # Generate case reference
        case_id = f"CASE{random.randint(100000, 999999)}"
        
        # Determine urgency
        urgent_keywords = ["stolen", "lost", "unauthorized", "fraud", "block", "immediate"]
        is_urgent = any(keyword in description.lower() for keyword in urgent_keywords)
        
        if is_urgent:
            priority = "HIGH"
            response_time = "Immediate (Card blocked within 5 minutes)"
            bullets = [
                f"🚨 **URGENT CASE REGISTERED**",
                f"Case ID: **{case_id}**",
                f"Status: Card blocked immediately",
                "",
                "**Immediate Actions Taken:**",
                "✓ Your card has been blocked",
                "✓ No further transactions possible",
                "✓ Security team notified",
                "",
                "**Next Steps:**",
                "1. Check your recent transactions in the app",
                "2. Report unauthorized transactions",
                "3. Request new card (arrives in 5-7 days)",
                "4. Set up transaction alerts",
                "",
                "**Refund Process:**",
                "• Investigation: 7-10 business days",
                "• Temporary credit: 3-5 days (if eligible)",
                "• Final resolution: 30-45 days",
                "",
                f"📞 Emergency: 1800-XXX-BLOCK (24x7)",
                f"📧 Track status: demobank.com/disputes/{case_id}"
            ]
        else:
            priority = "NORMAL"
            response_time = "24-48 hours"
            bullets = [
                f"📋 **Dispute Case Registered**",
                f"Case ID: **{case_id}**",
                f"Transaction: {transaction_id}",
                "",
                "**Investigation Process:**",
                "1. Document review: 24-48 hours",
                "2. Merchant verification: 5-7 days",
                "3. Decision & resolution: 15-30 days",
                "",
                "**What You Can Do:**",
                "• Upload supporting documents",
                "• Provide additional details",
                "• Track case status online",
                "",
                "**Required Documents:**",
                "• Transaction receipt (if available)",
                "• Communication with merchant",
                "• Police report (for fraud cases)",
                "",
                f"📞 Contact: 1800-XXX-HELP",
                f"📧 Updates: disputes@demobank.com",
                f"🌐 Track: demobank.com/disputes/{case_id}"
            ]
        
        return {
            "summary": f"{'🚨 URGENT: Card blocked immediately!' if is_urgent else 'Dispute case registered.'} "
                      f"Your case ID is {case_id}. Expected response time: {response_time}.",
            "bullets": bullets,
            "data": {
                "case_id": case_id,
                "transaction_id": transaction_id,
                "priority": priority,
                "status": "CARD_BLOCKED" if is_urgent else "UNDER_REVIEW",
                "created_at": datetime.now().isoformat(),
                "expected_resolution": response_time,
                "is_urgent": is_urgent
            }
        }
    except Exception as e:
        return {
            "summary": f"Error processing dispute: {str(e)}",
            "bullets": [
                "Please call our 24x7 helpline immediately:",
                "📞 1800-XXX-BLOCK (for card blocking)",
                "📞 1800-XXX-HELP (for disputes)"
            ],
            "data": {"error": str(e)}
        }

