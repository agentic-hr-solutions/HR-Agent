"""Integration tests for the complete onboarding workflow."""

import pytest
from datetime import datetime, timedelta
from backend.agents.graph import build_onboarding_graph
from backend.agents.state import OnboardingState
from backend.agents.it_agent import IT_TASKS
from backend.agents.hr_agent import HR_TASKS


class TestOnboardingGraph:
    """Tests for the complete LangGraph workflow."""
    
    def test_graph_compiles_successfully(self):
        """Test that the graph compiles without errors."""
        graph = build_onboarding_graph()
        assert graph is not None
    
    def test_full_workflow_execution(self):
        """Test executing the full workflow from start to finish."""
        graph = build_onboarding_graph()
        
        # Create initial state with HR tasks pending
        initial_state: OnboardingState = {
            "new_hire_id": "test-001",
            "new_hire_name": "Test User",
            "email": "test@example.com",
            "role": "Engineer",
            "department": "Engineering",
            "start_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
            "manager_id": "mgr-001",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [t["id"] for t in HR_TASKS],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        # Execute the graph
        result = graph.invoke(initial_state)
        
        # Verify phase was determined
        assert result["current_phase"] == "pre_onboarding"
        
        # Verify HR tasks were completed
        assert len(result["completed_tasks"]) == len(HR_TASKS)
        
        # Verify messages were added
        assert len(result["messages"]) > 0
    
    def test_it_phase_workflow(self):
        """Test workflow in IT provisioning phase."""
        graph = build_onboarding_graph()
        
        # Create state for active_preparation phase (IT tasks)
        initial_state: OnboardingState = {
            "new_hire_id": "test-002",
            "new_hire_name": "IT Test User",
            "email": "it-test@example.com",
            "role": "Developer",
            "department": "Engineering",
            "start_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "manager_id": "mgr-002",
            "current_phase": "active_preparation",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [t["id"] for t in IT_TASKS],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = graph.invoke(initial_state)
        
        # Verify IT tasks were completed
        assert all(task_id in result["completed_tasks"] for task_id in [t["id"] for t in IT_TASKS])
        
        # Verify pending tasks cleared
        assert len(result["pending_tasks"]) == 0
    
    def test_empty_pending_tasks_completes(self):
        """Test that workflow completes when no pending tasks."""
        graph = build_onboarding_graph()
        
        initial_state: OnboardingState = {
            "new_hire_id": "test-003",
            "new_hire_name": "Complete User",
            "email": "complete@example.com",
            "role": "Manager",
            "department": "Operations",
            "start_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "manager_id": "mgr-003",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [],  # No pending tasks
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = graph.invoke(initial_state)
        
        # Should complete immediately
        assert result is not None
        assert len(result["pending_tasks"]) == 0


class TestWorkflowStateTransitions:
    """Tests for state transitions in the workflow."""
    
    def test_coordinator_to_agent_transition(self):
        """Test that coordinator properly routes to agents."""
        graph = build_onboarding_graph()
        
        # State that should route to HR agent
        state: OnboardingState = {
            "new_hire_id": "test-004",
            "new_hire_name": "Routing Test",
            "email": "routing@example.com",
            "role": "Engineer",
            "department": "IT",
            "start_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
            "manager_id": "mgr-004",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": ["hr-001"],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = graph.invoke(state)
        
        # HR agent should have processed the task
        assert "hr-001" in result["completed_tasks"]
        
        # Verify message mentions HR Agent
        hr_messages = [m for m in result["messages"] if "HR Agent" in m.content]
        assert len(hr_messages) > 0
