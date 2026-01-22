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
