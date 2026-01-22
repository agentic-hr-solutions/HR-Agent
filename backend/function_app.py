"""Azure Functions entry point for HR Onboarding API."""

import json
import logging
from datetime import datetime
from typing import Any

import azure.functions as func

from agents.graph import onboarding_graph
from agents.state import OnboardingState
from agents.it_agent import IT_TASKS
from agents.hr_agent import HR_TASKS
from agents.manager_agent import MANAGER_TASKS
from agents.training_agent import TRAINING_TASKS

app = func.FunctionApp()
logger = logging.getLogger(__name__)

# CORS headers for frontend integration
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json"
}


def create_initial_state(data: dict[str, Any]) -> OnboardingState:
    """Create initial onboarding state from request data."""
    now = datetime.utcnow().isoformat()
    
    # Collect all task IDs as pending
    all_task_ids = (
        [t["id"] for t in IT_TASKS] +
        [t["id"] for t in HR_TASKS] +
        [t["id"] for t in MANAGER_TASKS] +
        [t["id"] for t in TRAINING_TASKS]
    )
    
    state: OnboardingState = {
        "new_hire_id": data.get("id", f"nh-{datetime.utcnow().timestamp()}"),
        "new_hire_name": data["name"],
        "email": data.get("email", f"{data['name'].lower().replace(' ', '.')}@company.com"),
        "role": data["role"],
        "department": data.get("department", "General"),
        "start_date": data["start_date"],
        "manager_id": data.get("manager_id", "mgr-default"),
        "current_phase": "pre_onboarding",
        "tasks": [],
        "completed_tasks": [],
        "pending_tasks": all_task_ids,
        "messages": [],
        "created_at": now,
        "updated_at": now,
        "errors": [],
    }
    
    return state


def serialize_state(state: OnboardingState) -> dict[str, Any]:
    """Convert state to JSON-serializable dict."""
    return {
        "new_hire_id": state["new_hire_id"],
        "new_hire_name": state["new_hire_name"],
        "email": state["email"],
        "role": state["role"],
        "department": state["department"],
        "start_date": state["start_date"],
        "manager_id": state["manager_id"],
        "current_phase": state["current_phase"],
        "tasks": state["tasks"],
        "completed_tasks": state["completed_tasks"],
        "pending_tasks": state["pending_tasks"],
        "messages": [m.content if hasattr(m, 'content') else str(m) for m in state.get("messages", [])],
        "created_at": state["created_at"],
        "updated_at": state["updated_at"],
        "errors": state["errors"],
    }


@app.route(route="onboarding/create", methods=["POST", "OPTIONS"])
def create_onboarding(req: func.HttpRequest) -> func.HttpResponse:
    """
    Create new onboarding workflow.
    
    POST /api/onboarding/create
    Body: {
        "name": "John Doe",
        "role": "Engineer",
        "start_date": "2026-02-15",
        "department": "Engineering",
        "manager_id": "mgr-001"
    }
    """
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers=CORS_HEADERS
        )
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Validate required fields
        required_fields = ["name", "role", "start_date"]
        missing_fields = [f for f in required_fields if f not in req_body]
        if missing_fields:
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required fields",
                    "missing": missing_fields
                }),
                status_code=400,
                headers=CORS_HEADERS
            )
        
        # Create initial state
        initial_state = create_initial_state(req_body)
        
        # Execute the workflow
        logger.info(f"Starting onboarding for {initial_state['new_hire_name']}")
        result_state = onboarding_graph.invoke(initial_state)
        
        # Serialize response
        response_data = serialize_state(result_state)
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=201,
            headers=CORS_HEADERS
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid request body", "detail": str(e)}),
            status_code=400,
            headers=CORS_HEADERS
        )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "detail": str(e)}),
            status_code=500,
            headers=CORS_HEADERS
        )


@app.route(route="onboarding/{id}", methods=["GET", "OPTIONS"])
def get_onboarding(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get onboarding status by ID.
    
    GET /api/onboarding/{id}
    """
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers=CORS_HEADERS
        )
    
    try:
        onboarding_id = req.route_params.get('id')
        
        # TODO: Implement Cosmos DB lookup
        # For now, return a mock response
        return func.HttpResponse(
            json.dumps({
                "error": "Not implemented",
                "message": "Cosmos DB integration pending",
                "id": onboarding_id
            }),
            status_code=501,
            headers=CORS_HEADERS
        )
        
    except Exception as e:
        logger.error(f"Error fetching onboarding: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers=CORS_HEADERS
        )


@app.route(route="onboarding/{id}/advance", methods=["PUT", "OPTIONS"])
def advance_onboarding(req: func.HttpRequest) -> func.HttpResponse:
    """
    Advance onboarding to next phase.
    
    PUT /api/onboarding/{id}/advance
    """
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers=CORS_HEADERS
        )
    
    try:
        onboarding_id = req.route_params.get('id')
        
        # TODO: Implement workflow advancement
        return func.HttpResponse(
            json.dumps({
                "error": "Not implemented",
                "message": "Workflow advancement pending",
                "id": onboarding_id
            }),
            status_code=501,
            headers=CORS_HEADERS
        )
        
    except Exception as e:
        logger.error(f"Error advancing onboarding: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers=CORS_HEADERS
        )


@app.route(route="onboarding/{id}/status", methods=["GET", "OPTIONS"])
def get_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get quick status summary.
    
    GET /api/onboarding/{id}/status
    """
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers=CORS_HEADERS
        )
    
    try:
        onboarding_id = req.route_params.get('id')
        
        # TODO: Implement status lookup
        return func.HttpResponse(
            json.dumps({
                "error": "Not implemented",
                "message": "Status lookup pending",
                "id": onboarding_id
            }),
            status_code=501,
            headers=CORS_HEADERS
        )
        
    except Exception as e:
        logger.error(f"Error fetching status: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers=CORS_HEADERS
        )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "hr-onboarding-api",
            "timestamp": datetime.utcnow().isoformat()
        }),
        status_code=200,
        headers=CORS_HEADERS
    )
