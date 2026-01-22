"""Unit tests for the Coordinator Agent."""

import pytest
from datetime import datetime, timedelta
from backend.agents.coordinator import (
    coordinator_agent,
    calculate_days_until_start,
    determine_phase,
    should_continue,
)
from backend.agents.state import OnboardingState


class TestCalculateDaysUntilStart:
    """Tests for calculate_days_until_start function."""
    
    def test_future_date(self):
        """Test with a future start date."""
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        days = calculate_days_until_start(future_date)
        assert days == 10
    
    def test_past_date(self):
        """Test with a past start date."""
        past_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        days = calculate_days_until_start(past_date)
        assert days == -5
    
    def test_today(self):
        """Test with today's date."""
        today = datetime.now().strftime("%Y-%m-%d")
        days = calculate_days_until_start(today)
        assert days == 0


class TestDeterminePhase:
    """Tests for determine_phase function."""
    
    def test_pre_onboarding_phase(self):
        """Test pre_onboarding phase (>14 days)."""
        assert determine_phase(15) == "pre_onboarding"
        assert determine_phase(30) == "pre_onboarding"
    
    def test_active_preparation_phase(self):
        """Test active_preparation phase (7-14 days)."""
        assert determine_phase(8) == "active_preparation"
        assert determine_phase(14) == "active_preparation"
    
    def test_immediate_prep_phase(self):
        """Test immediate_prep phase (0-7 days)."""
        assert determine_phase(0) == "immediate_prep"
        assert determine_phase(7) == "immediate_prep"
    
    def test_post_start_phase(self):
        """Test post_start phase (negative days)."""
        assert determine_phase(-1) == "post_start"
        assert determine_phase(-10) == "post_start"


class TestCoordinatorAgent:
    """Tests for coordinator_agent function."""
    
    def test_sets_phase_correctly(self):
        """Test that coordinator sets the correct phase."""
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        state: OnboardingState = {
            "new_hire_id": "001",
            "new_hire_name": "John Doe",
            "email": "john@example.com",
            "role": "Engineer",
            "department": "Engineering",
            "start_date": future_date,
            "manager_id": "mgr-001",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = coordinator_agent(state)
        
        assert result["current_phase"] == "active_preparation"
        assert len(result["messages"]) == 1
        assert "John Doe" in result["messages"][0].content
    
    def test_updates_timestamp(self):
        """Test that coordinator updates the timestamp."""
        future_date = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        state: OnboardingState = {
            "new_hire_id": "001",
            "new_hire_name": "Jane Doe",
            "email": "jane@example.com",
            "role": "Manager",
            "department": "Operations",
            "start_date": future_date,
            "manager_id": "mgr-002",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": "2026-01-01T00:00:00",
            "errors": [],
        }
        
        result = coordinator_agent(state)
        
        assert result["updated_at"] != "2026-01-01T00:00:00"


class TestShouldContinue:
    """Tests for should_continue routing function."""
    
    def test_no_pending_tasks_returns_complete(self):
        """Test that empty pending tasks returns complete."""
        state: OnboardingState = {
            "new_hire_id": "001",
            "new_hire_name": "Test",
            "email": "test@example.com",
            "role": "Engineer",
            "department": "IT",
            "start_date": "2026-02-01",
            "manager_id": "mgr-001",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        assert should_continue(state) == "complete"
    
    def test_pre_onboarding_routes_to_hr(self):
        """Test pre_onboarding phase routes to HR agent."""
        state: OnboardingState = {
            "new_hire_id": "001",
            "new_hire_name": "Test",
            "email": "test@example.com",
            "role": "Engineer",
            "department": "IT",
            "start_date": "2026-02-01",
            "manager_id": "mgr-001",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": ["task-1"],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        assert should_continue(state) == "hr_agent"
    
    def test_active_preparation_routes_to_it(self):
        """Test active_preparation phase routes to IT agent."""
        state: OnboardingState = {
            "new_hire_id": "001",
            "new_hire_name": "Test",
            "email": "test@example.com",
            "role": "Engineer",
            "department": "IT",
            "start_date": "2026-02-01",
            "manager_id": "mgr-001",
            "current_phase": "active_preparation",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": ["task-1"],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        assert should_continue(state) == "it_agent"
