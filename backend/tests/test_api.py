"""API integration tests for Azure Functions endpoints."""

import json
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Mock Azure Functions for testing
import sys
from unittest.mock import MagicMock
sys.modules['azure'] = MagicMock()
sys.modules['azure.functions'] = MagicMock()

import azure.functions as func
from backend.function_app import (
    create_onboarding,
    get_onboarding,
    health_check,
    create_initial_state,
    serialize_state,
)
from backend.agents.state import OnboardingState


class TestCreateInitialState:
    """Tests for create_initial_state helper."""
    
    def test_creates_valid_state(self):
        """Test creating initial state from request data."""
        data = {
            "name": "John Doe",
            "role": "Engineer",
            "start_date": "2026-02-15",
            "department": "Engineering",
            "manager_id": "mgr-001"
        }
        
        state = create_initial_state(data)
        
        assert state["new_hire_name"] == "John Doe"
        assert state["role"] == "Engineer"
        assert state["start_date"] == "2026-02-15"
        assert state["department"] == "Engineering"
        assert state["manager_id"] == "mgr-001"
        assert state["current_phase"] == "pre_onboarding"
        assert len(state["pending_tasks"]) == 20  # All tasks pending
    
    def test_generates_defaults(self):
        """Test that defaults are generated for optional fields."""
        data = {
            "name": "Jane Smith",
            "role": "Manager",
            "start_date": "2026-03-01"
        }
        
        state = create_initial_state(data)
        
        assert state["department"] == "General"
        assert state["manager_id"] == "mgr-default"
        assert "@company.com" in state["email"]


class TestSerializeState:
    """Tests for serialize_state helper."""
    
    def test_serializes_state_correctly(self):
        """Test state serialization to JSON-compatible dict."""
        from langchain_core.messages import HumanMessage
        
        state: OnboardingState = {
            "new_hire_id": "nh-001",
            "new_hire_name": "Test User",
            "email": "test@company.com",
            "role": "Engineer",
            "department": "IT",
            "start_date": "2026-02-01",
            "manager_id": "mgr-001",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": ["it-001"],
            "pending_tasks": ["it-002"],
            "messages": [HumanMessage(content="Test message")],
            "created_at": "2026-01-22T00:00:00",
            "updated_at": "2026-01-22T01:00:00",
            "errors": [],
        }
        
        result = serialize_state(state)
        
        assert result["new_hire_id"] == "nh-001"
        assert result["messages"] == ["Test message"]
        assert isinstance(result, dict)


class TestHealthCheckEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check_returns_200(self):
        """Test health check returns healthy status."""
        mock_req = Mock(spec=func.HttpRequest)
        
        response = health_check(mock_req)
        
        assert response.status_code == 200
        body = json.loads(response.get_body())
        assert body["status"] == "healthy"
        assert body["service"] == "hr-onboarding-api"


class TestCreateOnboardingEndpoint:
    """Tests for create onboarding endpoint."""
    
    @patch('backend.function_app.onboarding_graph')
    def test_creates_onboarding_successfully(self, mock_graph):
        """Test successful onboarding creation."""
        # Mock request
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.method = "POST"
        mock_req.get_json.return_value = {
            "name": "Alice Brown",
            "role": "Developer",
            "start_date": "2026-02-20"
        }
        
        # Mock graph execution
        mock_result = {
            "new_hire_id": "nh-001",
            "new_hire_name": "Alice Brown",
            "email": "alice.brown@company.com",
            "role": "Developer",
            "department": "General",
            "start_date": "2026-02-20",
            "manager_id": "mgr-default",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        mock_graph.invoke.return_value = mock_result
        
        response = create_onboarding(mock_req)
        
        assert response.status_code == 201
        body = json.loads(response.get_body())
        assert body["new_hire_name"] == "Alice Brown"
        assert body["role"] == "Developer"
    
    def test_returns_400_for_missing_fields(self):
        """Test validation of required fields."""
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.method = "POST"
        mock_req.get_json.return_value = {
            "name": "Bob"
            # Missing role and start_date
        }
        
        response = create_onboarding(mock_req)
        
        assert response.status_code == 400
        body = json.loads(response.get_body())
        assert "error" in body
        assert "missing" in body
    
    def test_handles_cors_preflight(self):
        """Test CORS preflight OPTIONS request."""
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.method = "OPTIONS"
        
        response = create_onboarding(mock_req)
        
        assert response.status_code == 204
        assert "Access-Control-Allow-Origin" in response.headers


class TestGetOnboardingEndpoint:
    """Tests for get onboarding endpoint."""
    
    def test_returns_not_implemented(self):
        """Test that GET endpoint returns 501 (not implemented yet)."""
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.method = "GET"
        mock_req.route_params = {"id": "nh-001"}
        
        response = get_onboarding(mock_req)
        
        assert response.status_code == 501
        body = json.loads(response.get_body())
        assert "Not implemented" in body["error"]


class TestAPIIntegration:
    """Integration tests for complete API flow."""
    
    @patch('backend.function_app.onboarding_graph')
    def test_full_api_workflow(self, mock_graph):
        """Test complete workflow from API request to response."""
        # Setup mock
        future_date = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        
        mock_graph.invoke.return_value = {
            "new_hire_id": "nh-integration-test",
            "new_hire_name": "Integration Test",
            "email": "integration@test.com",
            "role": "Engineer",
            "department": "Engineering",
            "start_date": future_date,
            "manager_id": "mgr-test",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": ["hr-001", "hr-002"],
            "pending_tasks": [],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        # Create request
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.method = "POST"
        mock_req.get_json.return_value = {
            "name": "Integration Test",
            "role": "Engineer",
            "start_date": future_date,
            "department": "Engineering"
        }
        
        # Execute
        response = create_onboarding(mock_req)
        
        # Verify
        assert response.status_code == 201
        body = json.loads(response.get_body())
        
        assert body["new_hire_name"] == "Integration Test"
        assert body["current_phase"] == "pre_onboarding"
        assert "hr-001" in body["completed_tasks"]
        assert len(body["completed_tasks"]) == 2
