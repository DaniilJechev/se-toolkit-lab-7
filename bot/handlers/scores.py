"""Handler for /scores command."""
import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from services.lms_client import LMSClient


async def handle_scores(lms: "LMSClient", lab_name: Optional[str] = None) -> str:
    """
    Handle the /scores command.
    
    Args:
        lms: LMS API client instance.
        lab_name: Optional lab name to filter scores.
    
    Returns:
        Scores information with per-task pass rates.
    """
    if not lab_name:
        return "📊 Usage: /scores lab-XX\n\nExample: /scores lab-04"
    
    # Normalize lab name (lab-04, lab04, lab 04 -> lab-04)
    lab_name = lab_name.lower().strip()
    match = re.search(r'lab[- ]?(\d+)', lab_name, re.IGNORECASE)
    if match:
        lab_num = match.group(1).zfill(2)
        lab_name = f"lab-{lab_num}"
    
    try:
        # Get pass rates from backend
        pass_rates = await lms.get_pass_rates(lab_name)
        
        if not pass_rates:
            # Try to get items and check if lab exists
            items = await lms.get_items()
            labs = [item for item in items if item.get("type") == "lab"]
            lab_ids = [f"lab-{str(lab.get('id', '')).zfill(2)}" for lab in labs[:5]]
            
            return f"📊 No pass rate data for {lab_name}.\n\nAvailable: {', '.join(lab_ids)}"
        
        # Format pass rates - backend returns: task, avg_score, attempts
        lines = [f"📊 Pass rates for {lab_name.title()}:\n"]
        for task_data in pass_rates:
            task_name = task_data.get("task", "Unknown Task")
            avg_score = task_data.get("avg_score", 0)
            attempts = task_data.get("attempts", 0)
            lines.append(f"• {task_name}: {avg_score:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
    
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "connect" in error_msg.lower():
            return "❌ Backend error: connection refused. Check that the services are running."
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return "❌ Backend error: HTTP 401 Unauthorized. Check LMS_API_KEY."
        elif "404" in error_msg:
            return f"❌ Lab {lab_name} not found."
        else:
            return f"❌ Backend error: {error_msg[:100]}"
