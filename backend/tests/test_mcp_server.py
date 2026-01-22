"""Tests for LangGraph MCP Server."""

import pytest
from mcp_server import (
    NewHireInput,
    OnboardingStatus,
    TaskList,
    PhaseInfo,
    mcp,
)


class TestMCPServerModels:
    """Test Pydantic models."""

    def test_new_hire_input_valid(self):
        """Test valid NewHireInput creation."""
        input_data = NewHireInput(
            name="Jane Doe",
            role="Backend Engineer",
            start_date="2026-02-01",
            manager="John Smith",
            location="Remote",
        )
        assert input_data.name == "Jane Doe"
        assert input_data.role == "Backend Engineer"
        assert input_data.email is None

    def test_new_hire_input_with_email(self):
        """Test NewHireInput with optional email."""
        input_data = NewHireInput(
            name="Jane Doe",
            role="Backend Engineer",
            start_date="2026-02-01",
            manager="John Smith",
            location="Remote",
            email="jane@company.com",
        )
        assert input_data.email == "jane@company.com"

    def test_onboarding_status_creation(self):
        """Test OnboardingStatus model."""
        status = OnboardingStatus(
            new_hire_id="NH-001",
            name="Jane Doe",
            role="Engineer",
            start_date="2026-02-01",
            phase="pre_onboarding",
            tasks_completed=["welcome_email"],
            tasks_pending=["setup_workspace"],
            days_until_start=10,
        )
        assert status.new_hire_id == "NH-001"
        assert len(status.tasks_completed) == 1
        assert len(status.tasks_pending) == 1

    def test_task_list_model(self):
        """Test TaskList model."""
        tasks = TaskList(
            completed=["task1", "task2"],
            pending=["task3"],
            total=3,
        )
        assert tasks.total == 3
        assert len(tasks.completed) == 2

    def test_phase_info_model(self):
        """Test PhaseInfo model."""
        info = PhaseInfo(
            current_phase="pre_onboarding",
            available_phases=["pre_onboarding", "active_preparation"],
            phase_description="Initial phase",
        )
        assert info.current_phase == "pre_onboarding"
        assert len(info.available_phases) == 2


class TestMCPServerTools:
    """Test MCP server tools."""

    @pytest.mark.skip(reason="Requires full backend implementation")
    def test_create_onboarding_tool(self):
        """Test create_onboarding tool."""
        # This test requires the full backend to be implemented
        pass

    @pytest.mark.skip(reason="Requires database implementation")
    def test_get_status_tool(self):
        """Test get_onboarding_status tool."""
        # This test requires Cosmos DB implementation
        pass

    @pytest.mark.skip(reason="Requires database implementation")
    def test_list_tasks_tool(self):
        """Test list_tasks tool."""
        # This test requires Cosmos DB implementation
        pass

    @pytest.mark.skip(reason="Requires database implementation")
    def test_get_phase_info_tool(self):
        """Test get_phase_info tool."""
        # This test requires Cosmos DB implementation
        pass

    @pytest.mark.skip(reason="Requires database implementation")
    def test_advance_phase_tool(self):
        """Test advance_phase tool."""
        # This test requires Cosmos DB implementation
        pass


class TestMCPServerResources:
    """Test MCP server resources."""

    @pytest.mark.skip(reason="Requires database implementation")
    def test_onboarding_resource(self):
        """Test onboarding resource retrieval."""
        # This test requires Cosmos DB implementation
        pass


class TestMCPServerPrompts:
    """Test MCP server prompts."""

    def test_create_onboarding_prompt(self):
        """Test create onboarding prompt generation."""
        from mcp_server import create_onboarding_prompt

        messages = create_onboarding_prompt(
            name="Jane Doe",
            role="Engineer",
            start_date="2026-02-01",
        )
        assert len(messages) == 2
        assert "Jane Doe" in messages[0].content
        assert "Engineer" in messages[0].content

    def test_check_status_prompt(self):
        """Test check status prompt generation."""
        from mcp_server import check_status_prompt

        messages = check_status_prompt(new_hire_id="NH-001")
        assert len(messages) == 2
        assert "NH-001" in messages[0].content


class TestIntegrationPlaceholders:
    """Test integration placeholders."""

    def test_cosmos_db_get_state(self):
        """Test Cosmos DB get_state placeholder."""
        from integrations.cosmos_db import get_onboarding_state

        # Should return mock data
        state = get_onboarding_state("test-id")
        assert state is not None
        assert state["new_hire_id"] == "test-id"
        assert "phase" in state

    def test_cosmos_db_save_state(self):
        """Test Cosmos DB save_state placeholder."""
        from integrations.cosmos_db import save_onboarding_state

        # Should not raise error (placeholder)
        save_onboarding_state({"test": "data"})


class TestMCPServerConfiguration:
    """Test MCP server configuration."""

    def test_server_name(self):
        """Test server has correct name."""
        assert mcp.name == "HR Onboarding Agent"

    def test_server_has_tools(self):
        """Test server has registered tools."""
        # FastMCP automatically registers tools via decorators
        # We can verify by checking the module has the expected functions
        from mcp_server import (
            create_onboarding,
            get_onboarding_status,
            list_tasks,
            get_phase_info,
            advance_phase,
        )
        
        assert callable(create_onboarding)
        assert callable(get_onboarding_status)
        assert callable(list_tasks)
        assert callable(get_phase_info)
        assert callable(advance_phase)

    def test_server_has_resources(self):
        """Test server has registered resources."""
        from mcp_server import get_onboarding_resource
        
        assert callable(get_onboarding_resource)

    def test_server_has_prompts(self):
        """Test server has registered prompts."""
        from mcp_server import create_onboarding_prompt, check_status_prompt
        
        assert callable(create_onboarding_prompt)
        assert callable(check_status_prompt)


@pytest.mark.integration
class TestMCPEndToEnd:
    """End-to-end integration tests (requires full implementation)."""

    @pytest.mark.skip(reason="Requires Phase 2 completion")
    def test_full_onboarding_workflow(self):
        """Test complete onboarding workflow through MCP."""
        # 1. Create onboarding
        # 2. Check status
        # 3. List tasks
        # 4. Advance phase
        # 5. Verify completion
        pass
