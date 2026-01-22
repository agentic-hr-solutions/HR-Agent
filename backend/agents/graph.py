"""LangGraph orchestrator for the onboarding workflow."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from .state import OnboardingState
from .coordinator import coordinator_agent, should_continue
from .it_agent import it_agent
from .hr_agent import hr_agent
from .manager_agent import manager_agent
from .training_agent import training_agent


def build_onboarding_graph() -> CompiledStateGraph:
    """
    Build the onboarding workflow graph.
    
    Flow:
    1. Coordinator determines phase
    2. Route to appropriate agent based on phase
    3. Continue until all tasks complete
    
    Returns:
        Compiled LangGraph with invoke() method
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
