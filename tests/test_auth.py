"""Tests for the authentication module."""

import pytest

from auth.authenticator import authenticate, AuthResult


class TestAuthenticate:
    def test_valid_domain(self):
        result = authenticate("user@financecommander.com")
        assert result.success is True
        assert result.user_email == "user@financecommander.com"
        assert result.error_message is None

    def test_invalid_domain(self):
        result = authenticate("user@example.com")
        assert result.success is False
        assert result.user_email is None
        assert "Access denied" in result.error_message

    def test_invalid_email_format(self):
        result = authenticate("invalid-email")
        assert result.success is False
        assert result.user_email is None
        assert result.error_message == "Invalid email format"

    def test_empty_email(self):
        result = authenticate("")
        assert result.success is False
        assert result.user_email is None
        assert result.error_message == "Invalid email format"

    def test_case_insensitive_domain(self):
        result = authenticate("user@FINANCECOMMANDER.COM")
        assert result.success is True
        assert result.user_email == "user@FINANCECOMMANDER.COM"