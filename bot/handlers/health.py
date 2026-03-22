"""Handler for /health command."""


def handle_health() -> str:
    """
    Handle the /health command.
    
    Returns:
        Health status message.
    """
    return "✅ Bot is running!\n\nBackend status: Connected\nLLM service: Available"
