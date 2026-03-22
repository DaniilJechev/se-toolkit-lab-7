"""Handler for /labs command."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.lms_client import LMSClient


async def handle_labs(lms: "LMSClient") -> str:
    """
    Handle the /labs command.
    
    Args:
        lms: LMS API client instance.
    
    Returns:
        List of available labs from backend.
    """
    try:
        items = await lms.get_items()
        
        if not items:
            return "📚 No labs available. Run ETL sync to populate data."
        
        # Filter only lab-type items
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "📚 No labs found in the system."
        
        # Format lab list
        lab_lines = []
        for lab in labs:
            title = lab.get("title", "Unknown Lab")
            lab_id = lab.get("id", "?")
            lab_lines.append(f"• {title}")
        
        return "📚 Available Labs:\n\n" + "\n".join(lab_lines) + "\n\nUse /scores lab-XX for detailed info."
    
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "connect" in error_msg.lower():
            return "❌ Backend error: connection refused. Check that the services are running."
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return "❌ Backend error: HTTP 401 Unauthorized. Check LMS_API_KEY."
        else:
            return f"❌ Backend error: {error_msg[:100]}"
