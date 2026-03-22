"""Default handler for unknown commands."""


def handle_unknown(command: str) -> str:
    """
    Handle unknown commands or messages.
    
    Args:
        command: The unknown command or message text.
    
    Returns:
        Helpful fallback message.
    """
    return (
        f"❓ Unknown command: {command}\n\n"
        "I didn't understand that. Try one of these:\n\n"
        "/start - Welcome message\n"
        "/help - Available commands\n"
        "/labs - List labs\n"
        "/scores - Check scores\n"
        "/health - System status"
    )
