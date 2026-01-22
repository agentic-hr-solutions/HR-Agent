# Execute Phase 2: Backend Implementation

This prompt executes Phase 2 of the automated workflow - implementing all LangGraph agents.

## Pre-requisites

- Phase 1 completed (project structure exists)
- Skills available: github-issues, microsoft-code-reference, microsoft-docs

## Execution Order

### Task 2.1: Create OnboardingState Model

**Skill Chain**:
1. `github-issues` → Update issue "[Backend] Create OnboardingState model" to in_progress
2. `microsoft-code-reference` → Query "TypedDict LangGraph state pattern"

**Implementation**:

Create `backend/agents/state.py`:

```python
"""Onboarding state model for the multi-agent system."""

from datetime import date
from typing import Annotated, Literal, TypedDict

from langgraph.graph import add_messages


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
```

**Complete**: `github-issues` → Close issue with implementation details

---

### Task 2.2: Implement Coordinator Agent

**Skill Chain**:
1. `github-issues` → Update issue to in_progress
2. `microsoft-code-reference` → Query "LangGraph conditional edge routing"

**Implementation**:

Create `backend/agents/coordinator.py`:

```python
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
```

---

### Task 2.3: Implement IT Agent

Create `backend/agents/it_agent.py`:

```python
"""IT Agent - handles IT provisioning tasks."""

from datetime import datetime
from langchain_core.messages import HumanMessage

from .state import OnboardingState, Task


IT_TASKS = [
    {"id": "it-001", "name": "Create email account", "category": "it"},
    {"id": "it-002", "name": "Provision laptop", "category": "it"},
    {"id": "it-003", "name": "Create access badge", "category": "it"},
    {"id": "it-004", "name": "Setup software accounts", "category": "it"},
    {"id": "it-005", "name": "Configure VPN access", "category": "it"},
]


def it_agent(state: OnboardingState) -> OnboardingState:
    """
    IT Agent that handles technology provisioning.
    
    Tasks:
    - Email account creation
    - Laptop provisioning
    - Access badge creation
    - Software account setup
    - VPN configuration
    """
    completed_tasks = list(state.get("completed_tasks", []))
    tasks = list(state.get("tasks", []))
    messages_to_add = []
    
    for task_def in IT_TASKS:
        if task_def["id"] not in completed_tasks:
            # Simulate task completion
            task: Task = {
                **task_def,
                "status": "completed",
                "assigned_to": "IT Department",
                "due_date": state["start_date"],
                "completed_at": datetime.utcnow().isoformat(),
                "notes": f"Auto-provisioned for {state['new_hire_name']}"
            }
            tasks.append(task)
            completed_tasks.append(task_def["id"])
            
            messages_to_add.append(HumanMessage(
                content=f"[IT Agent] Completed: {task_def['name']} for {state['new_hire_name']}"
            ))
    
    # Update pending tasks
    pending_tasks = [
        t for t in state.get("pending_tasks", []) 
        if t not in completed_tasks
    ]
    
    return {
        **state,
        "tasks": tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "updated_at": datetime.utcnow().isoformat(),
        "messages": messages_to_add,
    }
```

---

### Task 2.4: Implement HR Agent

Create `backend/agents/hr_agent.py`:

```python
"""HR Agent - handles HR processing tasks."""

from datetime import datetime
from langchain_core.messages import HumanMessage

from .state import OnboardingState, Task


HR_TASKS = [
    {"id": "hr-001", "name": "Send offer letter", "category": "hr"},
    {"id": "hr-002", "name": "Collect personal documents", "category": "hr"},
    {"id": "hr-003", "name": "Process background check", "category": "hr"},
    {"id": "hr-004", "name": "Setup payroll", "category": "hr"},
    {"id": "hr-005", "name": "Enroll in benefits", "category": "hr"},
]


def hr_agent(state: OnboardingState) -> OnboardingState:
    """
    HR Agent that handles human resources processing.
    
    Tasks:
    - Offer letter management
    - Document collection
    - Background check processing
    - Payroll setup
    - Benefits enrollment
    """
    completed_tasks = list(state.get("completed_tasks", []))
    tasks = list(state.get("tasks", []))
    messages_to_add = []
    
    for task_def in HR_TASKS:
        if task_def["id"] not in completed_tasks:
            task: Task = {
                **task_def,
                "status": "completed",
                "assigned_to": "HR Department",
                "due_date": state["start_date"],
                "completed_at": datetime.utcnow().isoformat(),
                "notes": f"Processed for {state['new_hire_name']}"
            }
            tasks.append(task)
            completed_tasks.append(task_def["id"])
            
            messages_to_add.append(HumanMessage(
                content=f"[HR Agent] Completed: {task_def['name']} for {state['new_hire_name']}"
            ))
    
    pending_tasks = [
        t for t in state.get("pending_tasks", []) 
        if t not in completed_tasks
    ]
    
    return {
        **state,
        "tasks": tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "updated_at": datetime.utcnow().isoformat(),
        "messages": messages_to_add,
    }
```

---

### Task 2.5: Implement Manager Agent

Create `backend/agents/manager_agent.py`:

```python
"""Manager Agent - handles manager-related onboarding tasks."""

from datetime import datetime
from langchain_core.messages import HumanMessage

from .state import OnboardingState, Task


MANAGER_TASKS = [
    {"id": "mgr-001", "name": "Schedule welcome 1:1", "category": "manager"},
    {"id": "mgr-002", "name": "Assign mentor/buddy", "category": "manager"},
    {"id": "mgr-003", "name": "Create 30-60-90 day plan", "category": "manager"},
    {"id": "mgr-004", "name": "Plan first week schedule", "category": "manager"},
    {"id": "mgr-005", "name": "Introduce to team", "category": "manager"},
]


def manager_agent(state: OnboardingState) -> OnboardingState:
    """
    Manager Agent that handles manager-related tasks.
    
    Tasks:
    - Welcome meeting scheduling
    - Mentor assignment
    - 30-60-90 day planning
    - First week scheduling
    - Team introduction planning
    """
    completed_tasks = list(state.get("completed_tasks", []))
    tasks = list(state.get("tasks", []))
    messages_to_add = []
    
    for task_def in MANAGER_TASKS:
        if task_def["id"] not in completed_tasks:
            task: Task = {
                **task_def,
                "status": "completed",
                "assigned_to": state["manager_id"],
                "due_date": state["start_date"],
                "completed_at": datetime.utcnow().isoformat(),
                "notes": f"Prepared for {state['new_hire_name']}"
            }
            tasks.append(task)
            completed_tasks.append(task_def["id"])
            
            messages_to_add.append(HumanMessage(
                content=f"[Manager Agent] Completed: {task_def['name']} for {state['new_hire_name']}"
            ))
    
    pending_tasks = [
        t for t in state.get("pending_tasks", []) 
        if t not in completed_tasks
    ]
    
    return {
        **state,
        "tasks": tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "updated_at": datetime.utcnow().isoformat(),
        "messages": messages_to_add,
    }
```

---

### Task 2.6: Implement Training Agent

Create `backend/agents/training_agent.py`:

```python
"""Training Agent - handles training and development tasks."""

from datetime import datetime
from langchain_core.messages import HumanMessage

from .state import OnboardingState, Task


TRAINING_TASKS = [
    {"id": "trn-001", "name": "Enroll in mandatory training", "category": "training"},
    {"id": "trn-002", "name": "Schedule orientation session", "category": "training"},
    {"id": "trn-003", "name": "Setup learning management access", "category": "training"},
    {"id": "trn-004", "name": "Assign compliance courses", "category": "training"},
    {"id": "trn-005", "name": "Create personalized learning path", "category": "training"},
]


def training_agent(state: OnboardingState) -> OnboardingState:
    """
    Training Agent that handles learning and development.
    
    Tasks:
    - Mandatory training enrollment
    - Orientation scheduling
    - LMS access setup
    - Compliance course assignment
    - Learning path creation
    """
    completed_tasks = list(state.get("completed_tasks", []))
    tasks = list(state.get("tasks", []))
    messages_to_add = []
    
    for task_def in TRAINING_TASKS:
        if task_def["id"] not in completed_tasks:
            task: Task = {
                **task_def,
                "status": "completed",
                "assigned_to": "L&D Department",
                "due_date": state["start_date"],
                "completed_at": datetime.utcnow().isoformat(),
                "notes": f"Enrolled {state['new_hire_name']}"
            }
            tasks.append(task)
            completed_tasks.append(task_def["id"])
            
            messages_to_add.append(HumanMessage(
                content=f"[Training Agent] Completed: {task_def['name']} for {state['new_hire_name']}"
            ))
    
    pending_tasks = [
        t for t in state.get("pending_tasks", []) 
        if t not in completed_tasks
    ]
    
    return {
        **state,
        "tasks": tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "updated_at": datetime.utcnow().isoformat(),
        "messages": messages_to_add,
    }
```

---

### Task 2.7: Create Graph Orchestrator

**Skill Chain**:
1. `microsoft-code-reference` → Query "LangGraph StateGraph with conditional edges"

Create `backend/agents/graph.py`:

```python
"""LangGraph orchestrator for the onboarding workflow."""

from langgraph.graph import StateGraph, END

from .state import OnboardingState
from .coordinator import coordinator_agent, should_continue
from .it_agent import it_agent
from .hr_agent import hr_agent
from .manager_agent import manager_agent
from .training_agent import training_agent


def build_onboarding_graph() -> StateGraph:
    """
    Build the onboarding workflow graph.
    
    Flow:
    1. Coordinator determines phase
    2. Route to appropriate agent based on phase
    3. Continue until all tasks complete
    
    Returns:
        Compiled LangGraph StateGraph
    """
    # Create the graph
    workflow = StateGraph(OnboardingState)
    
    # Add nodes
    workflow.add_node("coordinator", coordinator_agent)
    workflow.add_node("it_agent", it_agent)
    workflow.add_node("hr_agent", hr_agent)
    workflow.add_node("manager_agent", manager_agent)
    workflow.add_node("training_agent", training_agent)
    
    # Set entry point
    workflow.set_entry_point("coordinator")
    
    # Add conditional edges from coordinator
    workflow.add_conditional_edges(
        "coordinator",
        should_continue,
        {
            "it_agent": "it_agent",
            "hr_agent": "hr_agent",
            "manager_agent": "manager_agent",
            "training_agent": "training_agent",
            "complete": END,
        }
    )
    
    # Add edges from agents back to coordinator
    workflow.add_edge("it_agent", "coordinator")
    workflow.add_edge("hr_agent", "coordinator")
    workflow.add_edge("manager_agent", "coordinator")
    workflow.add_edge("training_agent", "coordinator")
    
    # Compile the graph
    return workflow.compile()


# Create default instance
onboarding_graph = build_onboarding_graph()
```

## Completion Criteria

Phase 2 is complete when:
- [ ] All agent files exist and are syntactically correct
- [ ] All files have type hints
- [ ] Graph compiles successfully
- [ ] All GitHub issues for Phase 2 are closed

## Validation Command

```bash
cd backend && python -c "from agents import build_onboarding_graph; g = build_onboarding_graph(); print('Graph compiled successfully!')"
```

## Next Phase

```
@hr-onboarding-orchestrator Execute Phase 3: API Implementation
```
