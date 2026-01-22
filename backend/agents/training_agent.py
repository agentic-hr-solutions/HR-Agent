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
