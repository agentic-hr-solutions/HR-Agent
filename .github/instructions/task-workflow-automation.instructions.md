---
applyTo: '**/*.py, **/backend/**'
description: 'Auto-generated task implementations following agentic workflow patterns'
---

# Task Implementation Workflow

This document defines how tasks are automatically implemented by the agentic workflow.

## Task Lifecycle

```
[Created] → [Assigned] → [In Progress] → [Review] → [Completed]
    ↓           ↓            ↓             ↓           ↓
 github-     Orchestrator   Agent      Quality      github-
 issues      assigns to    executes    Gate        issues
 creates     appropriate   implementation validates closes
```

## Skill-Driven Task Execution

### Step 1: Task Creation (github-issues skill)

When a new requirement is identified:

```markdown
Use skill: github-issues
Action: create
Title: "[{category}] {task_name}"
Body: |
  ## Description
  {requirement_description}
  
  ## Technical Approach
  {approach_determined_by_orchestrator}
  
  ## Files to Create/Modify
  - {file_list}
  
  ## Acceptance Criteria
  - [ ] {criterion_1}
  - [ ] {criterion_2}
  
  ## Dependencies
  - {dependency_list}
  
Labels: [{category}, priority-{level}]
Milestone: Phase {n}
```

### Step 2: Reference Lookup (microsoft-code-reference skill)

Before implementation, fetch patterns:

```markdown
Use skill: microsoft-code-reference
Query: "{technology} {pattern_type} implementation example"
Apply to: {target_file}

# Example queries:
- "LangGraph StateGraph node implementation"
- "Azure Functions HTTP trigger Python v2"
- "Cosmos DB async upsert Python"
- "FastAPI dependency injection pattern"
```

### Step 3: Documentation Lookup (microsoft-docs skill)

For configuration and best practices:

```markdown
Use skill: microsoft-docs
Query: "{product} {topic}"
Extract: {specific_sections}

# Example queries:
- "Azure Functions Python configuration options"
- "Cosmos DB consistency levels explained"
- "LangGraph checkpointer configuration"
```

### Step 4: Implementation (python-mcp-expert agent)

Delegate to specialized agent:

```markdown
Invoke agent: python-mcp-expert
Prompt: |
  Implement {component_name}:
  
  ## Context from Skills
  {reference_code_from_step_2}
  {docs_from_step_3}
  
  ## Requirements
  {requirements_from_issue}
  
  ## Output
  Create file: {file_path}
  Follow: {coding_standards}
```

### Step 5: Testing (pytest-coverage prompt)

After implementation:

```markdown
Use prompt: pytest-coverage
Target: {file_path}
Coverage Goal: 80%
Test Types:
  - Unit tests for pure functions
  - Integration tests for I/O operations
  - Edge case tests
```

### Step 6: Task Completion (github-issues skill)

Close the loop:

```markdown
Use skill: github-issues
Action: close
Issue: #{issue_number}
Comment: |
  ✅ Implementation complete
  
  ## Files Created
  - {file_list}
  
  ## Tests
  - {test_count} tests written
  - Coverage: {coverage}%
  
  ## Next Steps
  - {follow_up_tasks}
```

## Example: Implement Coordinator Agent

### Full Workflow Execution

```yaml
# Task: Implement Coordinator Agent
workflow_id: impl-coordinator-001

steps:
  - id: create_issue
    skill: github-issues
    action: create
    title: "[Backend] Implement Coordinator Agent"
    labels: [backend, priority-high]
    milestone: Phase 2
    body: |
      Implement the coordinator agent that determines onboarding phase.
      
      ## Requirements
      - Calculate days until start date
      - Determine phase: pre_onboarding, active_preparation, immediate_prep, post_start
      - Update state with current phase
      
      ## Acceptance Criteria
      - [ ] coordinator_agent function created
      - [ ] Type hints complete
      - [ ] Unit tests passing
      - [ ] Documentation added

  - id: lookup_pattern
    skill: microsoft-code-reference
    query: "LangGraph agent node function pattern"
    depends_on: create_issue
    
  - id: implement
    agent: python-mcp-expert
    depends_on: lookup_pattern
    prompt: |
      Create backend/agents/coordinator.py with:
      
      ```python
      from datetime import datetime
      from typing import TypedDict, Literal
      from .state import OnboardingState

      def coordinator_agent(state: OnboardingState) -> OnboardingState:
          """
          Coordinator agent that determines the onboarding phase.
          
          Phases:
          - pre_onboarding: >14 days before start
          - active_preparation: 7-14 days before start
          - immediate_prep: 0-7 days before start
          - post_start: after start date
          """
          # Implementation here
          pass
      ```
      
      Follow pattern from: {lookup_pattern.output}
      
  - id: write_tests
    prompt: pytest-coverage
    depends_on: implement
    target: backend/agents/coordinator.py
    coverage_goal: 80%
    
  - id: close_issue
    skill: github-issues
    action: close
    depends_on: write_tests
    issue: "{create_issue.output.issue_number}"
    comment: |
      ✅ Coordinator agent implemented
      
      Files: backend/agents/coordinator.py
      Tests: backend/tests/test_coordinator.py
      Coverage: {write_tests.output.coverage}%
```

## Parallel Task Execution

Some tasks can run in parallel:

```yaml
parallel_group:
  name: "Implement All Agents"
  tasks:
    - impl-coordinator-001
    - impl-it-agent-002
    - impl-hr-agent-003
    - impl-manager-agent-004
    - impl-training-agent-005
  
  depends_on:
    - state-model-created
    
  join_condition: all_complete
  
  on_complete:
    - skill: github-issues
      action: create
      title: "[Backend] Create Graph Orchestrator"
      body: "All agents implemented. Create the StateGraph."
```

## Error Handling

When a task fails:

```yaml
on_error:
  - skill: github-issues
    action: create
    title: "[Bug] {task_name} failed"
    labels: [bug, blocker]
    body: |
      ## Error
      {error_message}
      
      ## Context
      - Task: {task_name}
      - Step: {failed_step}
      - File: {file_path}
      
      ## Stack Trace
      ```
      {stack_trace}
      ```
      
  - action: notify_orchestrator
    message: "Task failed, manual intervention needed"
    
  - action: suggest_fix
    prompt: |
      Analyze error and suggest fix:
      - Error: {error_message}
      - Code: {relevant_code}
```

## Quality Gates

Before marking phase complete:

```yaml
quality_gate:
  phase: 2
  checks:
    - name: "All files exist"
      command: |
        ls backend/agents/coordinator.py
        ls backend/agents/it_agent.py
        ls backend/agents/hr_agent.py
        ls backend/agents/manager_agent.py
        ls backend/agents/training_agent.py
        
    - name: "No syntax errors"
      command: "python -m py_compile backend/agents/*.py"
      
    - name: "Type hints valid"
      command: "pyright backend/agents/"
      
    - name: "Tests pass"
      command: "pytest backend/tests/ -v"
      
    - name: "Coverage met"
      command: "pytest --cov=backend/agents --cov-fail-under=80"
      
  on_pass:
    - skill: github-issues
      action: create
      title: "[Milestone] Phase 2 Complete"
      labels: [milestone]
      
  on_fail:
    - action: list_failures
    - skill: github-issues
      action: create
      title: "[Blocker] Phase 2 Quality Gate Failed"
      labels: [blocker]
```

## Metrics Collection

Track workflow performance:

```yaml
metrics:
  task_completion_time:
    start: {task_start_timestamp}
    end: {task_end_timestamp}
    
  skill_invocations:
    github-issues: {count}
    microsoft-code-reference: {count}
    microsoft-docs: {count}
    
  agent_invocations:
    python-mcp-expert: {count}
    meta-agentic-project-scaffold: {count}
    
  quality_metrics:
    tests_written: {count}
    coverage_achieved: {percentage}
    issues_created: {count}
    issues_closed: {count}
```
