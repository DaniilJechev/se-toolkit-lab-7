"""Handler for /submissions command."""
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from services.lms_client import LMSClient


async def handle_submissions(lms: "LMSClient", lab_name: Optional[str] = None) -> str:
    """
    Handle the /submissions command.
    
    Args:
        lms: LMS API client instance.
        lab_name: Optional lab name to filter submissions.
    
    Returns:
        Submissions information message.
    """
    if not lab_name:
        return "📝 Usage: /submissions lab-XX\n\nExample: /submissions lab-04"
    
    try:
        # Get logs (submissions) from backend
        logs = await lms.get_logs()
        
        if not logs:
            return f"📝 No submissions found for {lab_name}."
        
        # Filter by lab if specified
        lab_logs = [log for log in logs if lab_name.lower() in str(log.get("lab", "")).lower()]
        
        if not lab_logs:
            return f"📝 No submissions found for {lab_name}."
        
        # Show recent submissions
        recent = lab_logs[:5]
        lines = [f"📝 Recent submissions for {lab_name}:\n"]
        for log in recent:
            user = log.get("user", "Unknown")
            status = log.get("status", "Unknown")
            lines.append(f"• {user}: {status}")
        
        return "\n".join(lines)
    
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower():
            return "❌ Backend error: connection refused. Check that the services are running."
        else:
            return f"❌ Backend error: {error_msg[:100]}"
