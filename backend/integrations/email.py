"""Email service for sending onboarding notifications."""

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message structure."""
    to: str
    subject: str
    body: str
    html_body: Optional[str] = None


class EmailService:
    """Service for sending onboarding emails."""
    
    def __init__(self):
        """Initialize email service."""
        self.from_address = os.environ.get("EMAIL_FROM", "noreply@company.com")
        self.enabled = os.environ.get("EMAIL_ENABLED", "false").lower() == "true"
    
    def send_welcome_email(self, name: str, email: str, start_date: str) -> bool:
        """Send welcome email to new hire."""
        message = EmailMessage(
            to=email,
            subject=f"Welcome to the team, {name}!",
            body=f"""Hi {name},

Welcome to the company! We're excited to have you join us on {start_date}.

Your onboarding process has been initiated. You'll receive updates as tasks are completed.

Best regards,
HR Team
""",
            html_body=f"""<html>
<body>
<h1>Welcome, {name}!</h1>
<p>We're excited to have you join us on <strong>{start_date}</strong>.</p>
<p>Your onboarding process has been initiated.</p>
<p>Best regards,<br>HR Team</p>
</body>
</html>"""
        )
        
        return self._send(message)
    
    def send_manager_notification(self, manager_email: str, new_hire_name: str, start_date: str) -> bool:
        """Notify manager about new hire."""
        message = EmailMessage(
            to=manager_email,
            subject=f"New Team Member: {new_hire_name}",
            body=f"""Hello,

{new_hire_name} will be joining your team on {start_date}.

Please ensure you're prepared for their arrival:
- Schedule welcome 1:1
- Assign a buddy/mentor
- Prepare first week schedule

Best regards,
HR Team
"""
        )
        
        return self._send(message)
    
    def _send(self, message: EmailMessage) -> bool:
        """Send email message."""
        if not self.enabled:
            logger.info(f"[EMAIL MOCK] To: {message.to}, Subject: {message.subject}")
            return True
        
        # TODO: Implement actual email sending (Azure Communication Services, SendGrid, etc.)
        logger.warning("Email sending not implemented, set EMAIL_ENABLED=true to use")
        return False


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service