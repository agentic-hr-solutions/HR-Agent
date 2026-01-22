# Agentic Workflow Executor

This prompt executes the automated agentic workflow for the HR Onboarding project.

## Mode Selection

Select execution mode based on your current phase:

1. **Full Automation**: Execute all phases sequentially
2. **Phase-specific**: Execute a single phase
3. **Task-specific**: Execute a single task

## Phase 1: Project Setup

```yaml
execute:
  phase: setup
  tasks:
    - name: "Initialize Project Structure"
      skill: null
      actions:
        - Create backend/ directory
        - Create backend/agents/ directory
        - Create backend/integrations/ directory
        - Create backend/tests/ directory
        - Create pyproject.toml
      
    - name: "Create GitHub Issues for All Tasks"
      skill: github-issues
      actions:
        - Create issue: "[Setup] Initialize project structure"
        - Create issue: "[Backend] Implement Coordinator Agent"
        - Create issue: "[Backend] Implement IT Agent"
        - Create issue: "[Backend] Implement HR Agent"
        - Create issue: "[Backend] Implement Manager Agent"
        - Create issue: "[Backend] Implement Training Agent"
        - Create issue: "[Backend] Create Azure Function endpoints"
        - Create issue: "[Testing] Write unit tests for all agents"
        - Create issue: "[Testing] Integration testing"
```

## Phase 2: Backend Implementation

```yaml
execute:
  phase: backend
  tasks:
    - name: "Lookup LangGraph Pattern"
      skill: microsoft-code-reference
      query: "LangGraph StateGraph agent implementation pattern"
      apply_to: backend/agents/
      
    - name: "Implement State Model"
      agent: python-mcp-expert
      prompt: |
        Create OnboardingState TypedDict with fields:
        - new_hire_name: str
        - role: str
        - department: str
        - start_date: str
        - manager_id: str
        - current_phase: str
        - tasks_completed: List[str]
        - pending_tasks: List[str]
        - messages: List[str]
      output: backend/agents/state.py
      
    - name: "Implement Coordinator Agent"
      agent: python-mcp-expert
      prompt: |
        Create coordinator_agent function that:
        - Takes OnboardingState
        - Calculates days_until_start
        - Returns phase based on:
          - >14 days: "pre_onboarding"
          - 7-14 days: "active_preparation"
          - 0-7 days: "immediate_prep"
          - <0 days: "post_start"
        - Updates state["current_phase"]
      output: backend/agents/coordinator.py
      skill_chain:
        - skill: github-issues
          action: update
          issue: "[Backend] Implement Coordinator Agent"
          status: in_progress
          
    - name: "Implement IT Agent"
      agent: python-mcp-expert
      prompt: |
        Create it_agent function that:
        - Sets up email account
        - Provisions laptop
        - Creates access badges
        - Sets up software accounts
        Returns updated state with tasks_completed
      output: backend/agents/it_agent.py
      
    - name: "Implement HR Agent"
      agent: python-mcp-expert
      prompt: |
        Create hr_agent function that:
        - Sends offer letter
        - Collects documents
        - Processes background check
        - Sets up payroll
        Returns updated state
      output: backend/agents/hr_agent.py
      
    - name: "Implement Manager Agent"
      agent: python-mcp-expert
      prompt: |
        Create manager_agent function that:
        - Schedules 1:1 meetings
        - Assigns mentor
        - Creates 30-60-90 day plan
        - Sets first week schedule
        Returns updated state
      output: backend/agents/manager_agent.py
      
    - name: "Implement Training Agent"
      agent: python-mcp-expert
      prompt: |
        Create training_agent function that:
        - Enrolls in mandatory training
        - Schedules orientation
        - Sets up learning path
        - Assigns compliance courses
        Returns updated state
      output: backend/agents/training_agent.py
      
    - name: "Create Graph Orchestrator"
      agent: python-mcp-expert
      prompt: |
        Create build_onboarding_graph function that:
        - Creates StateGraph with OnboardingState
        - Adds all agent nodes
        - Adds conditional edges based on phase
        - Compiles and returns the graph
      output: backend/agents/graph.py
```

## Phase 3: API Implementation

```yaml
execute:
  phase: api
  tasks:
    - name: "Lookup Azure Functions Pattern"
      skill: microsoft-code-reference
      query: "Azure Functions Python v2 HTTP trigger with JSON body"
      
    - name: "Lookup Cosmos DB Integration"
      skill: microsoft-docs
      query: "Azure Cosmos DB Python SDK async operations"
      
    - name: "Create Azure Function App"
      agent: python-mcp-expert
      prompt: |
        Create Azure Functions app with endpoints:
        - POST /api/onboarding/create
        - GET /api/onboarding/{id}
        - PUT /api/onboarding/{id}/advance
        - GET /api/onboarding/{id}/status
        
        Use Cosmos DB for state persistence
        Use the agent graph for processing
      output: backend/function_app.py
```

## Phase 4: Testing

```yaml
execute:
  phase: testing
  tasks:
    - name: "Create Test Fixtures"
      agent: python-mcp-expert
      prompt: |
        Create pytest fixtures for:
        - Sample OnboardingState objects
        - Mock Cosmos DB client
        - Test graph instance
      output: backend/tests/conftest.py
      
    - name: "Write Agent Tests"
      agent: python-mcp-expert
      skill: pytest-coverage
      prompt: |
        Write unit tests for all agents:
        - test_coordinator.py
        - test_it_agent.py
        - test_hr_agent.py
        - test_manager_agent.py
        - test_training_agent.py
        
        Target: 80% coverage
      output: backend/tests/
      
    - name: "Write Integration Tests"
      agent: python-mcp-expert
      prompt: |
        Write integration tests for:
        - Full graph execution
        - API endpoints
        - Cosmos DB integration
      output: backend/tests/test_integration.py
```

## Execution Command

To execute a phase, invoke the orchestrator agent:

```markdown
@hr-onboarding-orchestrator Execute Phase 2: Backend Implementation
- Start with state model
- Implement all agents in order
- Create tracking issues
- Update issues on completion
- Verify each implementation compiles
```

## Progress Tracking

After each task, update progress:

```markdown
Use skill: github-issues
Action: update
Issue: [Current task issue]
Status: completed
Comment: |
  ✅ Task completed
  Output: {file_path}
  Next: {next_task}
```

## Quality Gates

Before moving to next phase:

```yaml
quality_gates:
  phase_1_complete:
    - All directories created
    - pyproject.toml valid
    - GitHub issues created
    
  phase_2_complete:
    - All agent files created
    - All files have type hints
    - No syntax errors
    - Graph compiles successfully
    
  phase_3_complete:
    - All endpoints created
    - Endpoints return correct status codes
    - Cosmos DB integration working
    
  phase_4_complete:
    - All tests pass
    - Coverage >= 80%
    - No critical issues
```
