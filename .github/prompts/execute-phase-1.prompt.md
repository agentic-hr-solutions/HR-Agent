# Execute Phase 1: Project Setup

This prompt initiates Phase 1 of the automated workflow.

## Instructions

Execute these tasks in order:

### Task 1.1: Create Project Structure

Create the following directory structure:

```
backend/
├── agents/
│   ├── __init__.py
│   ├── state.py          # OnboardingState TypedDict
│   ├── coordinator.py    # Coordinator agent
│   ├── it_agent.py       # IT provisioning agent
│   ├── hr_agent.py       # HR processing agent
│   ├── manager_agent.py  # Manager tasks agent
│   ├── training_agent.py # Training enrollment agent
│   └── graph.py          # StateGraph orchestrator
├── integrations/
│   ├── __init__.py
│   ├── cosmos.py         # Cosmos DB client
│   └── email.py          # Email service
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures
│   └── test_agents/
│       └── __init__.py
└── function_app.py       # Azure Functions entry
```

### Task 1.2: Create pyproject.toml

Create `backend/pyproject.toml` with dependencies:

```toml
[project]
name = "hr-onboarding-agent"
version = "0.1.0"
description = "Employee Onboarding Agentic AI System"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2.0",
    "langchain-core>=0.3.0",
    "langchain-openai>=0.2.0",
    "azure-functions>=1.17.0",
    "azure-cosmos>=4.7.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.23.0",
    "pyright>=1.1.0",
    "ruff>=0.5.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
```

### Task 1.3: Create GitHub Issues for Phase 2

Use skill: github-issues

Create these issues:

1. **[Backend] Create OnboardingState model**
   - Labels: backend, priority-high
   - Milestone: Phase 2
   - Body: Define TypedDict with all state fields

2. **[Backend] Implement Coordinator Agent**
   - Labels: backend, priority-high
   - Milestone: Phase 2
   - Body: Agent that determines onboarding phase

3. **[Backend] Implement IT Agent**
   - Labels: backend
   - Milestone: Phase 2
   - Body: Agent for IT provisioning tasks

4. **[Backend] Implement HR Agent**
   - Labels: backend
   - Milestone: Phase 2
   - Body: Agent for HR processing tasks

5. **[Backend] Implement Manager Agent**
   - Labels: backend
   - Milestone: Phase 2
   - Body: Agent for manager-related tasks

6. **[Backend] Implement Training Agent**
   - Labels: backend
   - Milestone: Phase 2
   - Body: Agent for training enrollment

7. **[Backend] Create StateGraph Orchestrator**
   - Labels: backend, priority-high
   - Milestone: Phase 2
   - Depends on: All agent implementations
   - Body: Wire up all agents into LangGraph

### Task 1.4: Create Initial Files

Create empty `__init__.py` files and placeholder files:

**backend/agents/__init__.py**:
```python
"""HR Onboarding Agents - LangGraph-based multi-agent system."""

from .state import OnboardingState
from .coordinator import coordinator_agent
from .it_agent import it_agent
from .hr_agent import hr_agent
from .manager_agent import manager_agent
from .training_agent import training_agent
from .graph import build_onboarding_graph

__all__ = [
    "OnboardingState",
    "coordinator_agent",
    "it_agent",
    "hr_agent",
    "manager_agent",
    "training_agent",
    "build_onboarding_graph",
]
```

## Completion Criteria

Phase 1 is complete when:
- [ ] All directories exist
- [ ] pyproject.toml is valid (can be parsed)
- [ ] GitHub issues are created
- [ ] __init__.py files exist

## Next Phase

After Phase 1, proceed to:
```
@hr-onboarding-orchestrator Execute Phase 2: Backend Implementation
```
