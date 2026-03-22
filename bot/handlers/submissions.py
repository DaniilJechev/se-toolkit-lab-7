"""Handler for /submissions command."""


def handle_submissions(lab_name: str = None) -> str:
    """
    Handle the /submissions command.
    
    Args:
        lab_name: Optional lab name to filter submissions.
    
    Returns:
        Submissions information message.
    """
    if lab_name:
        return f"📝 Submissions for {lab_name}:\n\nNo recent submissions found.\n\nSubmit your work via the LMS."
    else:
        return (
            "📝 Recent Submissions:\n\n"
            "No recent submissions.\n\n"
            "Use /submissions lab-XX to check a specific lab."
        )
