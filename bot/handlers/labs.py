"""Handler for /labs command."""


def handle_labs() -> str:
    """
    Handle the /labs command.
    
    Returns:
        List of available labs.
    """
    return (
        "📚 Available Labs:\n\n"
        "• Lab 01 – Products, Architecture & Roles\n"
        "• Lab 02 – Requirements & Use Cases\n"
        "• Lab 03 – Domain Modeling\n"
        "• Lab 04 – Application Logic\n"
        "• Lab 05 – Data Persistence\n"
        "• Lab 06 – Testing & CI/CD\n"
        "• Lab 07 – Telegram Bot & LLM Integration\n\n"
        "Use /scores lab-XX to check your score for a specific lab."
    )
