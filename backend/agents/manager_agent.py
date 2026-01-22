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
