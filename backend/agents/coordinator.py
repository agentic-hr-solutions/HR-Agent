"""Coordinator agent - determines onboarding phase and routes to appropriate agents."""

from datetime import datetime, date
from typing import Literal

from langchain_core.messages import HumanMessage

from .state import OnboardingState


def calculate_days_until_start(start_date_str: str) -> int:
    """Calculate days between today and start date."""
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    today = date.today()
    return (start_date - today).days


def determine_phase(days_until_start: int) -> Literal[
    "pre_onboarding", "active_preparation", "immediate_prep", "post_start"
]:
    """Determine onboarding phase based on days until start."""
    if days_until_start > 14:
        return "pre_onboarding"
    elif days_until_start > 7:
        return "active_preparation"
    elif days_until_start >= 0:
        return "immediate_prep"
    else:
        return "post_start"


def coordinator_agent(state: OnboardingState) -> OnboardingState:
    """
    Coordinator agent that determines the onboarding phase.
    
    This agent:
    1. Calculates days until the new hire's start date
    2. Determines the appropriate onboarding phase
    3. Updates state with current phase
    4. Adds coordination message
    
    Args:
        state: Current onboarding state
        
    Returns:
        Updated state with current_phase set
    """
    days_until_start = calculate_days_until_start(state["start_date"])
    phase = determine_phase(days_until_start)
    
    message = HumanMessage(
        content=f"[Coordinator] New hire {state['new_hire_name']} is {days_until_start} days "
        f"from start date. Setting phase to: {phase}"
    )
    
    return {
        **state,
        "current_phase": phase,
        "updated_at": datetime.utcnow().isoformat(),
        "messages": [message],
    }


def should_continue(state: OnboardingState) -> str:
    """Determine next agent based on current phase and pending tasks."""
    phase = state["current_phase"]
    pending = state.get("pending_tasks", [])
    
    if not pending:
        return "complete"
    
    # Route based on phase and task type
    if phase == "pre_onboarding":
        return "hr_agent"
    elif phase == "active_preparation":
        return "it_agent"
    elif phase == "immediate_prep":
        return "manager_agent"
    elif phase == "post_start":
        return "training_agent"
    else:
        return "complete"
