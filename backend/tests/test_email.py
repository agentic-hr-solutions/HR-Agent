"""Tests for email service integration."""

import pytest
from unittest.mock import patch
from backend.integrations.email import EmailService, get_email_service, EmailMessage


class TestEmailService:
    """Tests for email service."""
    
    @patch.dict('os.environ', {'EMAIL_ENABLED': 'false'})
    def test_initialization(self):
        """Test email service initialization."""
        service = EmailService()
        
        assert service.from_address == "noreply@company.com"
        assert service.enabled is False
    
    @patch.dict('os.environ', {
        'EMAIL_ENABLED': 'true',
        'EMAIL_FROM': 'hr@company.com'
    })
    def test_initialization_with_env(self):
        """Test initialization with environment variables."""
        service = EmailService()
        
        assert service.from_address == "hr@company.com"
        assert service.enabled is True
    
    @patch.dict('os.environ', {'EMAIL_ENABLED': 'false'})
    def test_send_welcome_email(self):
        """Test sending welcome email."""
        service = EmailService()
        
        result = service.send_welcome_email(
            name="John Doe",
            email="john@example.com",
            start_date="2026-02-15"
        )
        
        assert result is True  # Mock mode returns True
    
    @patch.dict('os.environ', {'EMAIL_ENABLED': 'false'})
    def test_send_manager_notification(self):
        """Test sending manager notification."""
        service = EmailService()
        
        result = service.send_manager_notification(
            manager_email="manager@company.com",
            new_hire_name="Jane Smith",
            start_date="2026-03-01"
        )
        
        assert result is True


class TestEmailMessage:
    """Tests for EmailMessage dataclass."""
    
    def test_creates_message(self):
        """Test creating email message."""
        msg = EmailMessage(
            to="test@example.com",
            subject="Test Subject",
            body="Test body"
        )
        
        assert msg.to == "test@example.com"
        assert msg.subject == "Test Subject"
        assert msg.body == "Test body"
        assert msg.html_body is None
    
    def test_creates_message_with_html(self):
        """Test creating email with HTML body."""
        msg = EmailMessage(
            to="test@example.com",
            subject="Test",
            body="Plain text",
            html_body="<html><body>HTML</body></html>"
        )
        
        assert msg.html_body == "<html><body>HTML</body></html>"


class TestGetEmailService:
    """Tests for get_email_service singleton."""
    
    @patch.dict('os.environ', {'EMAIL_ENABLED': 'false'})
    def test_returns_singleton(self):
        """Test that get_email_service returns the same instance."""
        # Reset singleton
        import backend.integrations.email as email_module
        email_module._email_service = None
        
        service1 = get_email_service()
        service2 = get_email_service()
        
        assert service1 is service2
