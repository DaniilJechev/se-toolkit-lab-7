"""Handler for /scores command."""


def handle_scores(lab_name: str = None) -> str:
    """
    Handle the /scores command.
    
    Args:
        lab_name: Optional lab name to filter scores.
    
    Returns:
        Scores information message.
    """
    if lab_name:
        return f"📊 Scores for {lab_name}:\n\nScore: --/100\nStatus: Checking...\n\nUse the LMS dashboard for detailed information."
    else:
        return (
            "📊 Your Scores:\n\n"
            "Lab 01: --/100\n"
            "Lab 02: --/100\n"
            "Lab 03: --/100\n"
            "Lab 04: --/100\n"
            "Lab 05: --/100\n"
            "Lab 06: --/100\n"
            "Lab 07: --/100\n\n"
            "Use /scores lab-XX for detailed info."
        )
