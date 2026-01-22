"""LangGraph MCP Server for HR Onboarding Workflow.

This MCP server exposes the LangGraph onboarding workflow as tools that can be
invoked by GitHub Copilot or other MCP clients.
"""

import json
import logging
from datetime import datetime
from typing import Any

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("HR Onboarding Agent")


# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED INPUT/OUTPUT
# ============================================================================


class NewHireInput(BaseModel):
    """Input model for creating a new hire onboarding."""

    name: str = Field(description="Full name of the new hire")
    role: str = Field(description="Job role/title")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    manager: str = Field(description="Manager's name")
    location: str = Field(description="Work location (Remote, Onsite, or Hybrid)")
    email: str | None = Field(default=None, description="Email address (optional)")


class OnboardingStatus(BaseModel):
    """Output model for onboarding status."""

    new_hire_id: str = Field(description="Unique identifier for the new hire")
    new_hire_name: str = Field(description="New hire name")
    email: str = Field(description="Email address")
    role: str = Field(description="Job role")
    department: str = Field(description="Department")
    start_date: str = Field(description="Start date")
    current_phase: str = Field(description="Current onboarding phase")
    completed_tasks: list[str] = Field(description="List of completed task IDs")
    pending_tasks: list[str] = Field(description="List of pending task IDs")
    task_count: int = Field(description="Total number of tasks")
    days_until_start: int = Field(default=0, description="Days until start date")


class TaskList(BaseModel):
    """Model for task information."""

    completed: list[str] = Field(description="Completed tasks")
    pending: list[str] = Field(description="Pending tasks")
    total: int = Field(description="Total number of tasks")


class PhaseInfo(BaseModel):
    """Model for phase information."""

    current_phase: str = Field(description="Current onboarding phase")
    available_phases: list[str] = Field(description="All available phases")
    phase_description: str = Field(description="Description of current phase")


# ============================================================================
# MCP TOOLS
# ============================================================================


@mcp.tool()
def create_onboarding(input_data: NewHireInput) -> OnboardingStatus:
    """
    Create a new employee onboarding workflow.

    This tool initiates the multi-agent onboarding process for a new hire.
    The coordinator agent determines the appropriate phase, and specialist
    agents (IT, HR, Manager, Training) execute tasks autonomously.

    Args:
        input_data: New hire information including name, role, start date, etc.

    Returns:
        OnboardingStatus with phase, completed tasks, and pending tasks
    """
    try:
        # Import here to avoid circular dependencies
        from agents.state import OnboardingState
        from agents.graph import build_onboarding_graph

        # Calculate days until start
        start_date_obj = datetime.strptime(input_data.start_date, "%Y-%m-%d")
        today = datetime.now()
        days_until_start = (start_date_obj - today).days

        # Generate unique ID
        new_hire_id = f"NH-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create initial state matching the OnboardingState TypedDict
        from datetime import datetime as dt
        
        initial_state: OnboardingState = {
            "new_hire_id": new_hire_id,
            "new_hire_name": input_data.name,
            "email": input_data.email or f"{input_data.name.lower().replace(' ', '.')}@company.com",
            "role": input_data.role,
            "department": "Engineering",  # Default, can be made configurable
            "start_date": input_data.start_date,
            "manager_id": input_data.manager,
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "messages": [],
            "created_at": dt.now().isoformat(),
            "updated_at": dt.now().isoformat(),
            "errors": [],
        }

        # Build and invoke the graph (already compiled)
        graph = build_onboarding_graph()
        result = graph.invoke(initial_state)

        # Return structured output
        days_until_start = (datetime.strptime(result["start_date"], "%Y-%m-%d") - datetime.now()).days
        
        return OnboardingStatus(
            new_hire_id=result["new_hire_id"],
            new_hire_name=result["new_hire_name"],
            email=result["email"],
            role=result["role"],
            department=result["department"],
            start_date=result["start_date"],
            current_phase=result["current_phase"],
            completed_tasks=result["completed_tasks"],
            pending_tasks=result["pending_tasks"],
            task_count=len(result.get("tasks", [])),
            days_until_start=days_until_start,
        )

    except Exception as e:
        logger.error(f"Error creating onboarding: {e}")
        raise


@mcp.tool()
def get_onboarding_status(new_hire_id: str) -> OnboardingStatus:
    """
    Get the current status of an onboarding workflow.

    Args:
        new_hire_id: Unique identifier for the new hire (e.g., NH-20260122093000)

    Returns:
        OnboardingStatus with current phase and task status
    """
    try:
        # Import database integration
        from integrations.cosmos_db import get_onboarding_state

        # Retrieve state from database
        state = get_onboarding_state(new_hire_id)

        if not state:
            raise ValueError(f"Onboarding not found for ID: {new_hire_id}")

        days_until_start = (datetime.strptime(state["start_date"], "%Y-%m-%d") - datetime.now()).days
        
        return OnboardingStatus(
            new_hire_id=state["new_hire_id"],
            new_hire_name=state["new_hire_name"],
            email=state["email"],
            role=state["role"],
            department=state["department"],
            start_date=state["start_date"],
            current_phase=state["current_phase"],
            completed_tasks=state["completed_tasks"],
            pending_tasks=state["pending_tasks"],
            task_count=len(state.get("tasks", [])),
            days_until_start=days_until_start,
        )

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise


@mcp.tool()
def list_tasks(new_hire_id: str) -> TaskList:
    """
    List all tasks for a specific onboarding workflow.

    Args:
        new_hire_id: Unique identifier for the new hire

    Returns:
        TaskList with completed and pending tasks
    """
    try:
        from integrations.cosmos_db import get_onboarding_state

        state = get_onboarding_state(new_hire_id)

        if not state:
            raise ValueError(f"Onboarding not found for ID: {new_hire_id}")

        completed = state.get("tasks_completed", [])
        pending = state.get("tasks_pending", [])

        return TaskList(
            completed=completed,
            pending=pending,
            total=len(completed) + len(pending),
        )

    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise


@mcp.tool()
def get_phase_info(new_hire_id: str) -> PhaseInfo:
    """
    Get detailed information about the current onboarding phase.

    Args:
        new_hire_id: Unique identifier for the new hire

    Returns:
        PhaseInfo with current phase and description
    """
    try:
        from integrations.cosmos_db import get_onboarding_state

        state = get_onboarding_state(new_hire_id)

        if not state:
            raise ValueError(f"Onboarding not found for ID: {new_hire_id}")

        phase = state.get("current_phase", "unknown")
        
        # Phase descriptions
        phase_descriptions = {
            "pre_onboarding": "Initial preparation phase (>14 days before start)",
            "active_preparation": "Active preparation phase (7-14 days before start)",
            "immediate_prep": "Immediate preparation phase (0-7 days before start)",
            "day_one": "First day onboarding",
            "post_start": "Post-start integration phase",
            "complete": "Onboarding completed",
        }

        return PhaseInfo(
            current_phase=phase,
            available_phases=list(phase_descriptions.keys()),
            phase_description=phase_descriptions.get(phase, "Unknown phase"),
        )

    except Exception as e:
        logger.error(f"Error getting phase info: {e}")
        raise


@mcp.tool()
def advance_phase(new_hire_id: str) -> OnboardingStatus:
    """
    Manually advance the onboarding to the next phase.

    This tool triggers the coordinator agent to re-evaluate the phase
    and execute the next set of tasks.

    Args:
        new_hire_id: Unique identifier for the new hire

    Returns:
        Updated OnboardingStatus
    """
    try:
        from integrations.cosmos_db import get_onboarding_state
        from agents.graph import build_onboarding_graph

        # Get current state
        state = get_onboarding_state(new_hire_id)

        if not state:
            raise ValueError(f"Onboarding not found for ID: {new_hire_id}")

        # Re-run the graph with current state (already compiled)
        graph = build_onboarding_graph()
        result = graph.invoke(state)

        days_until_start = (datetime.strptime(result["start_date"], "%Y-%m-%d") - datetime.now()).days
        
        return OnboardingStatus(
            new_hire_id=result["new_hire_id"],
            new_hire_name=result["new_hire_name"],
            email=result["email"],
            role=result["role"],
            department=result["department"],
            start_date=result["start_date"],
            current_phase=result["current_phase"],
            completed_tasks=result["completed_tasks"],
            pending_tasks=result["pending_tasks"],
            task_count=len(result.get("tasks", [])),
            days_until_start=days_until_start,
        )

    except Exception as e:
        logger.error(f"Error advancing phase: {e}")
        raise


# ============================================================================
# MCP RESOURCES
# ============================================================================


@mcp.resource("onboarding://{new_hire_id}")
def get_onboarding_resource(new_hire_id: str) -> str:
    """
    Get complete onboarding information as a resource.

    This resource provides all available information about an onboarding
    workflow in a human-readable format.
    """
    try:
        from integrations.cosmos_db import get_onboarding_state

        state = get_onboarding_state(new_hire_id)

        if not state:
            return f"Onboarding not found for ID: {new_hire_id}"

        # Format as readable text
        days_until = (datetime.strptime(state['start_date'], "%Y-%m-%d") - datetime.now()).days
        
        return f"""
# Onboarding Status for {state['new_hire_name']}

**ID**: {state['new_hire_id']}
**Email**: {state['email']}
**Role**: {state['role']}
**Department**: {state['department']}
**Start Date**: {state['start_date']}
**Days Until Start**: {days_until}
**Current Phase**: {state['current_phase']}

## Completed Tasks ({len(state['completed_tasks'])})
{chr(10).join(f'✓ {task}' for task in state['completed_tasks'])}

## Pending Tasks ({len(state['pending_tasks'])})
{chr(10).join(f'⏳ {task}' for task in state['pending_tasks'])}

## Manager ID
{state.get('manager_id', 'Not assigned')}

## Total Tasks
{len(state.get('tasks', []))} tasks defined
"""

    except Exception as e:
        logger.error(f"Error getting resource: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# MCP PROMPTS
# ============================================================================


@mcp.prompt(title="Create New Hire Onboarding")
def create_onboarding_prompt(name: str, role: str, start_date: str) -> list:
    """
    Generate a prompt to create a new hire onboarding workflow.

    This prompt guides the user through creating an onboarding workflow
    with the necessary information.
    """
    from mcp.server.fastmcp.prompts import base

    return [
        base.UserMessage(f"""
I need to create an onboarding workflow for a new employee:

**Name**: {name}
**Role**: {role}
**Start Date**: {start_date}

Please use the create_onboarding tool to initiate the onboarding process.
You'll need to provide:
- Manager name
- Location (Remote/Onsite/Hybrid)
- Email address (optional)

Once created, the system will automatically:
1. Determine the appropriate onboarding phase
2. Assign tasks to specialist agents (IT, HR, Manager, Training)
3. Execute tasks autonomously
4. Track progress and completion
"""),
        base.AssistantMessage(
            "I'll help you create the onboarding workflow. "
            "I need a few more details: manager name and location."
        ),
    ]


@mcp.prompt(title="Check Onboarding Status")
def check_status_prompt(new_hire_id: str) -> list:
    """
    Generate a prompt to check onboarding status.
    """
    from mcp.server.fastmcp.prompts import base

    return [
        base.UserMessage(f"""
Please check the onboarding status for new hire ID: {new_hire_id}

Use the get_onboarding_status tool to retrieve:
- Current phase
- Completed tasks
- Pending tasks
- Days until start date

Provide a summary of the onboarding progress.
"""),
        base.AssistantMessage(
            f"I'll check the onboarding status for {new_hire_id}."
        ),
    ]


# ============================================================================
# SERVER CONFIGURATION
# ============================================================================


if __name__ == "__main__":
    # Run the MCP server
    # For stdio transport (default):
    mcp.run()
    
    # For HTTP transport (uncomment to use):
    # mcp.run(transport="streamable-http")
