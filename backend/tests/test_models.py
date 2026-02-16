"""Tests for database models and logging."""

import pytest
from datetime import datetime, timezone

from backend.models.usage_log import UsageLog


class TestUsageLog:
    """Test UsageLog model."""

    def test_create_usage_log(self, session):
        """Test creating a usage log entry."""
        log = UsageLog(
            user_email_hash="test_hash",
            specialist_id="test-specialist",
            specialist_name="Test Specialist",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            estimated_cost_usd=0.001,
            latency_ms=1234.5,
            success=True
        )
        
        session.add(log)
        session.commit()
        session.refresh(log)
        
        assert log.id is not None
        assert log.user_email_hash == "test_hash"
        assert log.specialist_id == "test-specialist"
        assert log.input_tokens == 100
        assert log.output_tokens == 50
        assert log.success is True

    def test_usage_log_timestamp(self, session):
        """Test that timestamp is set automatically."""
        log = UsageLog(
            user_email_hash="test_hash",
            specialist_id="test-specialist",
            specialist_name="Test Specialist",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            estimated_cost_usd=0.001,
            latency_ms=1234.5,
            success=True
        )
        
        session.add(log)
        session.commit()
        session.refresh(log)
        
        assert log.timestamp is not None
        assert isinstance(log.timestamp, datetime)

    def test_query_by_specialist(self, session):
        """Test querying logs by specialist ID."""
        # Create multiple logs
        log1 = UsageLog(
            user_email_hash="hash1",
            specialist_id="specialist-1",
            specialist_name="Specialist 1",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            estimated_cost_usd=0.001,
            latency_ms=1234.5,
            success=True
        )
        log2 = UsageLog(
            user_email_hash="hash2",
            specialist_id="specialist-2",
            specialist_name="Specialist 2",
            provider="anthropic",
            model="claude-3-opus",
            input_tokens=200,
            output_tokens=100,
            estimated_cost_usd=0.002,
            latency_ms=2345.6,
            success=True
        )
        log3 = UsageLog(
            user_email_hash="hash3",
            specialist_id="specialist-1",
            specialist_name="Specialist 1",
            provider="openai",
            model="gpt-4o",
            input_tokens=150,
            output_tokens=75,
            estimated_cost_usd=0.0015,
            latency_ms=1500.0,
            success=False
        )
        
        session.add_all([log1, log2, log3])
        session.commit()
        
        # Query for specialist-1
        from sqlmodel import select
        statement = select(UsageLog).where(UsageLog.specialist_id == "specialist-1")
        results = session.exec(statement).all()
        
        assert len(results) == 2
        assert all(log.specialist_id == "specialist-1" for log in results)

    def test_query_by_success(self, session):
        """Test querying logs by success status."""
        log1 = UsageLog(
            user_email_hash="hash1",
            specialist_id="test-specialist",
            specialist_name="Test Specialist",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            estimated_cost_usd=0.001,
            latency_ms=1234.5,
            success=True
        )
        log2 = UsageLog(
            user_email_hash="hash2",
            specialist_id="test-specialist",
            specialist_name="Test Specialist",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            estimated_cost_usd=0.001,
            latency_ms=1234.5,
            success=False
        )
        
        session.add_all([log1, log2])
        session.commit()
        
        # Query for successful logs
        from sqlmodel import select
        statement = select(UsageLog).where(UsageLog.success == True)
        results = session.exec(statement).all()
        
        assert len(results) == 1
        assert results[0].success is True
