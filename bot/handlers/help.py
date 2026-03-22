"""Handler for /help command."""


def handle_help() -> str:
    """
    Handle the /help command.
    
    Returns:
        Help message with available commands.
    """
    return (
        "📖 Available Commands:\n\n"
        "/start - Welcome message and quick start guide\n"
        "/labs - List all available labs\n"
        "/scores [lab_name] - Show scores for a specific lab\n"
        "/submissions [lab_name] - View recent submissions\n"
        "/health - Check backend and API status\n"
        "/help - Show this help message\n\n"
        "💡 You can also ask questions in natural language:\n"
        "• What labs are available?\n"
        "• Show my scores for lab 04\n"
        "• How many submissions do I have?"
    )
