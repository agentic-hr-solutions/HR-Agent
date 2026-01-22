"""Onboarding state model for the multi-agent system."""

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages


class Task(TypedDict):
    """Individual onboarding task."""
    
    id: str
    name: str
    category: Literal["it", "hr", "manager", "training"]
    status: Literal["pending", "in_progress", "completed", "blocked"]
    assigned_to: str | None
    due_date: str | None
    completed_at: str | None
    notes: str


class OnboardingState(TypedDict):
    """State for the onboarding workflow."""
    
    # New hire information
    new_hire_id: str
    new_hire_name: str
    email: str
    role: str
    department: str
    start_date: str
    manager_id: str
    
    # Workflow state
    current_phase: Literal[
        "pre_onboarding",
        "active_preparation", 
        "immediate_prep",
        "post_start",
        "completed"
    ]
    
    # Task tracking
    tasks: list[Task]
    completed_tasks: list[str]  # Task IDs
    pending_tasks: list[str]    # Task IDs
    
    # Agent communication
    messages: Annotated[list, add_messages]
    
    # Metadata
    created_at: str
    updated_at: str
    errors: list[str]
