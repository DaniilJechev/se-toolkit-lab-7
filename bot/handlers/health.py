"""Handler for /health command."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.lms_client import LMSClient


async def handle_health(lms: "LMSClient") -> str:
    """
    Handle the /health command.
    
    Args:
        lms: LMS API client instance.
    
    Returns:
        Health status message with backend info.
    """
    try:
        # Try to fetch items to check backend health
        items = await lms.get_items()
        item_count = len(items) if items else 0
        
        if item_count > 0:
            return f"✅ Backend is healthy. {item_count} items available."
        else:
            return "⚠️ Backend is running but no data found. Run ETL sync."
    
    except Exception as e:
        # Extract clean error message without traceback
        error_msg = str(e)
        error_type = type(e).__name__
        
        # Format user-friendly error with actual error details
        if "connection" in error_msg.lower() or "connect" in error_msg.lower():
            return f"❌ Backend error: connection refused. Check that the services are running."
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return f"❌ Backend error: HTTP 401 Unauthorized. Check LMS_API_KEY."
        elif "404" in error_msg:
            return f"❌ Backend error: HTTP 404 Not Found."
        elif "500" in error_msg or "502" in error_msg or "503" in error_msg:
            return f"❌ Backend error: HTTP {error_msg.split()[1] if error_msg.split() else 'error'}. The backend service may be down."
        else:
            return f"❌ Backend error: {error_type}. {error_msg[:100]}"
