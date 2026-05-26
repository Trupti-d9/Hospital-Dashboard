import os
import requests
import json
from dotenv import load_dotenv

# We can import the database aggregation logic to inject live context
from routes.analytics import get_dashboard_data
from models.database import SessionLocal

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
You are the AI Concierge for Aarogya Multi-Specialty Hospital.
You are speaking with the CEO. Provide actionable insights based on the real-time hospital data context provided.
Answer concisely in 2-4 sentences using Indian number formatting (lakhs, crores).
Be specific and use the numbers from the context.
"""

def query_rag(question: str) -> str:
    """
    Queries OpenRouter API with live SQL-based context.
    """
    if not OPENROUTER_API_KEY:
        return "Error: OpenRouter API key is missing. Please check your environment variables."

    # Fetch real data context
    db = SessionLocal()
    try:
        live_data = get_dashboard_data(db)
        
        # Build a concise context summary so we don't blow up token limits
        total_rev = sum(d["revenue"] for d in live_data["revenue"])
        total_cost = sum(d["opex"] for d in live_data["revenue"])
        top_dept = max(live_data["deptFinancials"], key=lambda x: x["profit"]) if live_data["deptFinancials"] else {}
        total_patients = sum(d["inpatient"] + d["outpatient"] for d in live_data["patients"])
        
        context_str = f"""
        Total Revenue: {total_rev}
        Total Cost: {total_cost}
        Net Profit: {total_rev - total_cost}
        Total Patients: {total_patients}
        Most Profitable Department: {top_dept.get('dept', 'N/A')} (Profit: {top_dept.get('profit', 0)})
        """
        
    except Exception as e:
        context_str = f"Live DB fetch failed: {str(e)}. Fallback context used."
    finally:
        db.close()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "anthropic/claude-3.5-sonnet", # Can be swapped via OpenRouter
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + f"\nContext:\n{context_str}"},
            {"role": "user", "content": question}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"OpenRouter API request failed: {e}"
