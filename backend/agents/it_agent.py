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
