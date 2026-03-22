"""Simple keyword-based fallback routing (no regex, no LLM)."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.lms_client import LMSClient


async def simple_route(user_message: str, lms: "LMSClient") -> str:
    """
    Simple keyword-based routing as fallback when LLM is unavailable.
    
    This uses only simple string matching - no regex, no LLM.
    """
    msg = user_message.lower()

    # Greeting - check for whole words only
    if msg in ["hello", "hi", "hey", "yo", "sup"] or msg.startswith("hello ") or msg.startswith("hi ") or msg.startswith("hey "):
        return "Hello! I can help you with LMS data. Try asking about labs, scores, or students."

    # Lowest/worst pass rate comparison
    if "lowest" in msg or "worst" in msg or "best" in msg or "highest" in msg:
        if "lab" in msg and ("pass" in msg or "rate" in msg or "score" in msg):
            # Get all labs and compare
            items = await lms.get_items()
            labs = [item for item in items if item.get("type") == "lab"]
            
            if not labs:
                return "No labs found."
            
            # Get pass rates for each lab
            lab_rates = []
            for lab in labs[:7]:  # Limit to first 7 labs
                lab_id = f"lab-{str(lab.get('id', '')).zfill(2)}"
                rates = await lms.get_pass_rates(lab_id)
                if rates:
                    avg = sum(t.get('avg_score', 0) for t in rates) / len(rates) if rates else 0
                    lab_rates.append((lab.get('title', lab_id), avg, lab_id))
            
            if not lab_rates:
                return "No pass rate data available."
            
            # Sort by average
            lab_rates.sort(key=lambda x: x[1], reverse=("best" in msg or "highest" in msg))
            
            if "lowest" in msg or "worst" in msg:
                result = lab_rates[0]  # Lowest
                return f"Based on the data, {result[0]} has the lowest average pass rate at {result[1]:.1f}%."
            else:
                result = lab_rates[0]  # Highest (after reverse sort)
                return f"Based on the data, {result[0]} has the highest average pass rate at {result[1]:.1f}%."

    # Labs
    if "lab" in msg and ("available" in msg or "list" in msg or "what" in msg):
        items = await lms.get_items()
        labs = [item for item in items if item.get("type") == "lab"]
        if labs:
            lab_list = "\n".join([f"• {lab.get('title', 'Unknown')}" for lab in labs[:10]])
            return f"📚 Available Labs:\n\n{lab_list}"
        return "No labs found."

    # Scores - use simple string matching for lab number
    if "score" in msg or "pass rate" in msg:
        # Extract lab number without regex
        lab_num = None
        for i in range(1, 20):
            if f"lab {i}" in msg or f"lab-{i}" in msg or f"lab{i}" in msg:
                lab_num = str(i).zfill(2)
                break
        
        if lab_num:
            lab = f"lab-{lab_num}"
            rates = await lms.get_pass_rates(lab)
            if rates:
                lines = [f"📊 Pass rates for {lab}:"]
                for t in rates:
                    lines.append(f"• {t.get('task', 'Unknown')}: {t.get('avg_score', 0):.1f}% ({t.get('attempts', 0)} attempts)")
                return "\n".join(lines)
        return "Specify a lab, e.g., 'scores for lab 04'"

    # Students/learners
    if "student" in msg or "learner" in msg or "enrolled" in msg:
        learners = await lms.get_learners()
        return f"📚 {len(learners)} students enrolled."

    # Top learners
    if "top" in msg and ("student" in msg or "learner" in msg):
        # Extract lab number without regex
        lab_num = None
        limit = 5
        for i in range(1, 20):
            if f"lab {i}" in msg or f"lab-{i}" in msg or f"lab{i}" in msg:
                lab_num = str(i).zfill(2)
                break
            if str(i) in msg and "top" in msg:
                limit = i
        
        if lab_num:
            lab = f"lab-{lab_num}"
            top = await lms.get_top_learners(lab, limit)
            if top:
                lines = [f"🏆 Top {len(top)} learners for {lab}:"]
                for i, t in enumerate(top, 1):
                    lines.append(f"{i}. Learner #{t.get('learner_id', '?')}: {t.get('avg_score', 0):.1f}% avg")
                return "\n".join(lines)
        return "Specify a lab, e.g., 'top 5 students in lab 04'"

    # Default
    return "I can help with: labs list, scores for a lab, student count. Try 'what labs are available?' or 'scores for lab 04'."
