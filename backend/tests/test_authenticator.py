"""
Tests for authenticator.
"""
import pytest
from backend.auth.authenticator import validate_domain, process_email
from backend.errors import AuthenticationError


class TestAuthenticator:
    """Tests for domain validation and email processing."""
    
    def test_validate_domain_valid(self):
        """Test validating a valid email domain."""
        assert validate_domain("user@financecommander.com") is True
    
    def test_validate_domain_invalid(self):
        """Test validating an invalid email domain."""
        assert validate_domain("user@example.com") is False
    
    def test_validate_domain_no_at_symbol(self):
        """Test validating email without @ symbol."""
        assert validate_domain("invalid-email") is False
    
    def test_validate_domain_empty(self):
        """Test validating empty email."""
        assert validate_domain("") is False
    
    def test_validate_domain_case_insensitive(self):
        """Test domain validation is case insensitive."""
        assert validate_domain("user@FINANCECOMMANDER.COM") is True
    
    def test_process_email_valid(self):
        """Test processing a valid email."""
        email = process_email("User@FinanceCommander.com")
        assert email == "user@financecommander.com"
    
    def test_process_email_strips_whitespace(self):
        """Test email processing strips whitespace."""
        email = process_email("  user@financecommander.com  ")
        assert email == "user@financecommander.com"
    
    def test_process_email_invalid_domain(self):
        """Test processing email with invalid domain raises error."""
        with pytest.raises(AuthenticationError) as exc_info:
            process_email("user@example.com")
        
        assert "Email domain not allowed" in str(exc_info.value)
    
    def test_process_email_no_domain(self):
        """Test processing email without domain raises error."""
        with pytest.raises(AuthenticationError):
            process_email("invalid-email")
