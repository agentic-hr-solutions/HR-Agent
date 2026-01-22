---
applyTo: '**/*.py, **/pyproject.toml, **/*.yml'
description: 'Instructions for using integrated skills in HR Onboarding agentic workflow'
---

# Skill Integration Instructions

These instructions guide how to use the integrated skills in the HR Onboarding Agentic AI development workflow.

## Available Skills

### 1. github-issues

**Purpose**: Automate GitHub issue creation and management

**Usage Pattern**:
```markdown
## Create Issue
Use skill: github-issues
Action: create
Title: [Issue Title]
Labels: [backend, frontend, testing, documentation, bug, enhancement]
Milestone: [Phase 1, Phase 2, Phase 3, Phase 4]
Body: |
  [Issue description]
  
  ## Acceptance Criteria
  - [ ] Criterion 1
  - [ ] Criterion 2
```

**Auto-triggers**:
- When a new task starts → Create tracking issue
- When a task completes → Close related issue
- When an error occurs → Create bug issue

**Example**:
```
Use skill: github-issues
Action: create
Title: "[Backend] Implement Coordinator Agent"
Labels: [backend, priority-high]
Milestone: Phase 2
Body: |
  Implement the coordinator agent that decides onboarding phase.
  
  ## Requirements
  - Takes OnboardingState as input
  - Calculates days_until_start
  - Sets phase based on logic
  
  ## Acceptance Criteria
  - [ ] Agent function created
  - [ ] Unit tests passing
  - [ ] Type hints complete
```

### 2. microsoft-code-reference

**Purpose**: Fetch code examples and patterns from Microsoft documentation

**Usage Pattern**:
```markdown
Use skill: microsoft-code-reference
Query: [Technology/Pattern name]
Context: [Current file or component being worked on]
Output: [Where to apply the reference]
```

**Best For**:
- Azure Functions patterns
- LangGraph/LangChain examples
- Cosmos DB integration
- Python async patterns

**Example**:
```
Use skill: microsoft-code-reference
Query: "Azure Functions HTTP trigger with JSON body parsing Python v2"
Context: backend/function_app.py
Output: Apply pattern to /api/onboarding/create endpoint
```

### 3. microsoft-docs

**Purpose**: Search and extract official Microsoft documentation

**Usage Pattern**:
```markdown
Use skill: microsoft-docs
Query: [Documentation topic]
Purpose: [Why you need this documentation]
Extract: [Specific sections needed]
```

**Best For**:
- Configuration guides
- API specifications
- Troubleshooting
- Best practices

**Example**:
```
Use skill: microsoft-docs
Query: "Azure Cosmos DB Python SDK connection string configuration"
Purpose: Setup database connection for onboarding states
Extract: Connection string format, authentication methods
```

### 4. make-skill-template

**Purpose**: Create new custom skills for project-specific automation

**Usage Pattern**:
```markdown
Use skill: make-skill-template
Skill Name: [new-skill-name]
Purpose: [What the skill does]
Triggers: [When to invoke]
Inputs: [Required parameters]
Outputs: [What it produces]
```

**When to Create New Skills**:
- Repetitive project-specific tasks
- Integration with internal systems
- Custom automation needs

**Example**:
```
Use skill: make-skill-template
Skill Name: onboarding-email-generator
Purpose: Generate welcome email templates for new hires
Triggers: When HR agent needs to send welcome email
Inputs: new_hire_name, role, start_date, manager_name
Outputs: HTML email template, plain text version
```

## Skill Chaining

Skills can be chained for complex workflows:

```markdown
## Workflow: Create and Track Agent Implementation

Step 1: Create tracking issue
Use skill: github-issues
Action: create
Title: "[Backend] Implement {agent_name} Agent"
Labels: [backend]

Step 2: Lookup implementation pattern
Use skill: microsoft-code-reference
Query: "LangGraph agent node implementation"
Context: backend/agents/

Step 3: Document the pattern
Use skill: microsoft-docs
Query: "LangGraph best practices state management"

Step 4: Implement (via python-mcp-expert agent)
Invoke agent: python-mcp-expert
Prompt: "Implement {agent_name} agent following the pattern from Step 2"

Step 5: Close issue on completion
Use skill: github-issues
Action: close
Issue: From Step 1
Comment: "Implemented in {file_path}"
```

## Automatic Skill Invocation

The orchestrator agent automatically invokes skills based on context:

| Context | Auto-Invoked Skill | Action |
|---------|-------------------|--------|
| Starting new task | github-issues | Create tracking issue |
| Need code pattern | microsoft-code-reference | Fetch example |
| Configuration question | microsoft-docs | Search documentation |
| Task completed | github-issues | Update/close issue |
| Error encountered | github-issues | Create bug issue |
| Repetitive task identified | make-skill-template | Suggest new skill |

## Skill Configuration

Each skill can be configured in the workflow file:

```yaml
skills:
  - id: github-issues
    path: .github/skills/github-issues
    enabled: true
    config:
      auto_create_issues: true
      auto_close_on_complete: true
      default_labels: [hr-onboarding]
      
  - id: microsoft-code-reference
    path: .github/skills/microsoft-code-reference
    enabled: true
    config:
      cache_results: true
      preferred_languages: [python]
      
  - id: microsoft-docs
    path: .github/skills/microsoft-docs
    enabled: true
    config:
      cache_duration: 3600
      preferred_products: [azure-functions, cosmos-db]
```

## Best Practices

1. **Use skills for automation, not replacement**
   - Skills augment your workflow, they don't replace thinking
   - Review skill outputs before applying

2. **Chain skills for complex tasks**
   - Break down complex tasks into skill invocations
   - Use outputs from one skill as inputs to another

3. **Create custom skills for repetitive tasks**
   - If you do something 3+ times, consider a skill
   - Keep skills focused and single-purpose

4. **Track everything with github-issues**
   - Every task should have an issue
   - Close issues when tasks complete
   - Use labels consistently

5. **Cache documentation lookups**
   - microsoft-docs results can be cached
   - Avoid repeated lookups for same topics

## Troubleshooting

### Skill not found
```
Error: Skill 'skill-name' not found
Solution: Verify skill exists in .github/skills/ directory
```

### Skill invocation failed
```
Error: Failed to invoke skill
Solution: Check skill SKILL.md for required inputs
```

### Rate limiting
```
Error: Rate limit exceeded
Solution: Enable caching, reduce invocation frequency
```
