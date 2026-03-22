"""Handler for /start command."""


def handle_start(user_name: str = "User") -> str:
    """
    Handle the /start command.
    
    Args:
        user_name: The name of the user (optional).
    
    Returns:
        Welcome message string.
    """
    return (
        f"👋 Welcome, {user_name}!\n\n"
        "I'm your LMS Assistant bot. I can help you with:\n\n"
        "📚 /labs - List available labs\n"
        "📊 /scores [lab] - Check your scores\n"
        "📝 /submissions [lab] - View recent submissions\n"
        "❓ /help - Show available commands\n"
        "💚 /health - Check system status\n\n"
        "You can also ask me questions in natural language!"
    )
