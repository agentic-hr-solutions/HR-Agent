"""Unit tests for all specialist agents (IT, HR, Manager, Training)."""

import pytest
from datetime import datetime
from backend.agents.it_agent import it_agent, IT_TASKS
from backend.agents.hr_agent import hr_agent, HR_TASKS
from backend.agents.manager_agent import manager_agent, MANAGER_TASKS
from backend.agents.training_agent import training_agent, TRAINING_TASKS
from backend.agents.state import OnboardingState


class TestITAgent:
    """Tests for IT Agent."""
    
    def test_completes_all_it_tasks(self):
        """Test that IT agent completes all IT tasks."""
        state: OnboardingState = {
            "new_hire_id": "001",
            "new_hire_name": "John Doe",
            "email": "john@example.com",
            "role": "Engineer",
            "department": "Engineering",
            "start_date": "2026-02-01",
            "manager_id": "mgr-001",
            "current_phase": "active_preparation",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [t["id"] for t in IT_TASKS],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = it_agent(state)
        
        assert len(result["tasks"]) == len(IT_TASKS)
        assert len(result["completed_tasks"]) == len(IT_TASKS)
        assert len(result["messages"]) == len(IT_TASKS)
        assert all(task["id"] in result["completed_tasks"] for task in IT_TASKS)
    
    def test_skips_already_completed_tasks(self):
        """Test that IT agent skips already completed tasks."""
        state: OnboardingState = {
            "new_hire_id": "001",
            "new_hire_name": "John Doe",
            "email": "john@example.com",
            "role": "Engineer",
            "department": "Engineering",
            "start_date": "2026-02-01",
            "manager_id": "mgr-001",
            "current_phase": "active_preparation",
            "tasks": [],
            "completed_tasks": ["it-001", "it-002"],
            "pending_tasks": ["it-003", "it-004", "it-005"],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = it_agent(state)
        
        # Should only create 3 new tasks (it-003, it-004, it-005)
        assert len(result["tasks"]) == 3
        assert len(result["completed_tasks"]) == 5  # 2 existing + 3 new


class TestHRAgent:
    """Tests for HR Agent."""
    
    def test_completes_all_hr_tasks(self):
        """Test that HR agent completes all HR tasks."""
        state: OnboardingState = {
            "new_hire_id": "002",
            "new_hire_name": "Jane Smith",
            "email": "jane@example.com",
            "role": "Manager",
            "department": "Operations",
            "start_date": "2026-02-15",
            "manager_id": "mgr-002",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [t["id"] for t in HR_TASKS],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = hr_agent(state)
        
        assert len(result["tasks"]) == len(HR_TASKS)
        assert len(result["completed_tasks"]) == len(HR_TASKS)
        assert all(task["status"] == "completed" for task in result["tasks"])


class TestManagerAgent:
    """Tests for Manager Agent."""
    
    def test_completes_all_manager_tasks(self):
        """Test that Manager agent completes all manager tasks."""
        state: OnboardingState = {
            "new_hire_id": "003",
            "new_hire_name": "Bob Johnson",
            "email": "bob@example.com",
            "role": "Developer",
            "department": "Engineering",
            "start_date": "2026-02-01",
            "manager_id": "mgr-003",
            "current_phase": "immediate_prep",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [t["id"] for t in MANAGER_TASKS],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = manager_agent(state)
        
        assert len(result["tasks"]) == len(MANAGER_TASKS)
        assert all(task["assigned_to"] == "mgr-003" for task in result["tasks"])


class TestTrainingAgent:
    """Tests for Training Agent."""
    
    def test_completes_all_training_tasks(self):
        """Test that Training agent completes all training tasks."""
        state: OnboardingState = {
            "new_hire_id": "004",
            "new_hire_name": "Alice Brown",
            "email": "alice@example.com",
            "role": "Analyst",
            "department": "Finance",
            "start_date": "2026-01-20",
            "manager_id": "mgr-004",
            "current_phase": "post_start",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [t["id"] for t in TRAINING_TASKS],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = training_agent(state)
        
        assert len(result["tasks"]) == len(TRAINING_TASKS)
        assert all(task["assigned_to"] == "L&D Department" for task in result["tasks"])
        assert len(result["completed_tasks"]) == len(TRAINING_TASKS)


class TestAgentIntegration:
    """Integration tests across multiple agents."""
    
    def test_task_completion_updates_pending(self):
        """Test that completing tasks updates pending_tasks list."""
        state: OnboardingState = {
            "new_hire_id": "005",
            "new_hire_name": "Charlie Davis",
            "email": "charlie@example.com",
            "role": "Engineer",
            "department": "IT",
            "start_date": "2026-02-01",
            "manager_id": "mgr-005",
            "current_phase": "active_preparation",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": ["it-001", "it-002"],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = it_agent(state)
        
        assert len(result["pending_tasks"]) == 0
        assert "it-001" in result["completed_tasks"]
        assert "it-002" in result["completed_tasks"]
