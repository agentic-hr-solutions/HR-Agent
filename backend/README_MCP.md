# LangGraph MCP Server for HR Onboarding

This MCP server exposes the HR Onboarding LangGraph workflow as tools that can be invoked by GitHub Copilot, Claude Desktop, or other MCP clients.

## Architecture

The MCP server provides a standardized interface to the multi-agent onboarding workflow:

```
┌─────────────────────────────────────────┐
│   MCP Client (Copilot/Claude)          │
└────────────────┬────────────────────────┘
                 │ (MCP Protocol)
                 ↓
┌─────────────────────────────────────────┐
│   LangGraph MCP Server                  │
│  ├─ Tools (create, status, tasks)      │
│  ├─ Resources (onboarding://)          │
│  └─ Prompts (templates)                │
└────────────────┬────────────────────────┘
                 │ (invoke)
                 ↓
┌─────────────────────────────────────────┐
│   LangGraph Workflow                    │
│  ├─ Coordinator Agent                  │
│  ├─ IT Agent                           │
│  ├─ HR Agent                           │
│  ├─ Manager Agent                      │
│  └─ Training Agent                     │
└─────────────────────────────────────────┘
```

## Installation

### 1. Install Dependencies

```bash
cd backend
uv add "mcp[cli]"
# or
pip install "mcp[cli]"
```

### 2. Install the MCP Server

```bash
# Using MCP CLI
uv run mcp install mcp_server.py

# Or manually add to MCP config (~/.config/mcp/config.json)
{
  "mcpServers": {
    "hr-onboarding": {
      "command": "uv",
      "args": ["run", "mcp_server.py"],
      "cwd": "/path/to/HR-Agent/backend"
    }
  }
}
```

## Available Tools

### 1. `create_onboarding`

Create a new employee onboarding workflow.

**Input**:
```json
{
  "name": "Jane Doe",
  "role": "Backend Engineer",
  "start_date": "2026-02-01",
  "manager": "John Smith",
  "location": "Remote",
  "email": "jane.doe@company.com"
}
```

**Output**:
```json
{
  "new_hire_id": "NH-20260122093000",
  "name": "Jane Doe",
  "role": "Backend Engineer",
  "start_date": "2026-02-01",
  "phase": "pre_onboarding",
  "tasks_completed": ["welcome_email_sent", "manager_notified"],
  "tasks_pending": ["setup_workspace", "enroll_training"],
  "days_until_start": 10
}
```

### 2. `get_onboarding_status`

Get the current status of an onboarding workflow.

**Input**:
```json
{
  "new_hire_id": "NH-20260122093000"
}
```

**Output**:
```json
{
  "new_hire_id": "NH-20260122093000",
  "name": "Jane Doe",
  "phase": "active_preparation",
  "tasks_completed": [...],
  "tasks_pending": [...],
  "days_until_start": 5
}
```

### 3. `list_tasks`

List all tasks for an onboarding workflow.

**Input**:
```json
{
  "new_hire_id": "NH-20260122093000"
}
```

**Output**:
```json
{
  "completed": ["welcome_email_sent", "manager_notified"],
  "pending": ["setup_workspace", "enroll_training"],
  "total": 4
}
```

### 4. `get_phase_info`

Get detailed information about the current phase.

**Input**:
```json
{
  "new_hire_id": "NH-20260122093000"
}
```

**Output**:
```json
{
  "current_phase": "pre_onboarding",
  "available_phases": ["pre_onboarding", "active_preparation", "immediate_prep", ...],
  "phase_description": "Initial preparation phase (>14 days before start)"
}
```

### 5. `advance_phase`

Manually advance to the next onboarding phase.

**Input**:
```json
{
  "new_hire_id": "NH-20260122093000"
}
```

**Output**: Updated `OnboardingStatus`

## Available Resources

### `onboarding://{new_hire_id}`

Get complete onboarding information in a human-readable format.

**Example**:
```
onboarding://NH-20260122093000
```

**Returns**:
```markdown
# Onboarding Status for Jane Doe

**ID**: NH-20260122093000
**Role**: Backend Engineer
**Start Date**: 2026-02-01
**Days Until Start**: 10
**Current Phase**: pre_onboarding

## Completed Tasks (2)
✓ welcome_email_sent
✓ manager_notified

## Pending Tasks (2)
⏳ setup_workspace
⏳ enroll_training

## Manager
John Smith

## Location
Remote
```

## Available Prompts

### 1. `create_onboarding_prompt`

Template for creating a new onboarding workflow.

**Parameters**:
- `name`: New hire name
- `role`: Job role
- `start_date`: Start date (YYYY-MM-DD)

### 2. `check_status_prompt`

Template for checking onboarding status.

**Parameters**:
- `new_hire_id`: Unique identifier

## Usage Examples

### With GitHub Copilot

```python
# In Copilot Chat:
"Use the hr-onboarding MCP server to create a new onboarding for:
- Name: Jane Doe
- Role: Backend Engineer
- Start Date: 2026-02-01
- Manager: John Smith
- Location: Remote"
```

### With Claude Desktop

```
# In Claude Desktop:
Create a new employee onboarding workflow for Jane Doe,
Backend Engineer, starting Feb 1, 2026, reporting to John Smith,
working remotely.
```

### Testing with MCP Inspector

```bash
# Run the MCP Inspector
uv run mcp dev mcp_server.py

# This opens a web interface to test tools, resources, and prompts
```

## Development

### Running Locally

```bash
# Stdio transport (default)
uv run python mcp_server.py

# HTTP transport
# Edit mcp_server.py and uncomment:
# mcp.run(transport="streamable-http")
```

### Testing

```bash
# Run unit tests
pytest tests/test_mcp_server.py -v

# Test with MCP Inspector
uv run mcp dev mcp_server.py
```

## Onboarding Phases

The coordinator agent determines phases based on `days_until_start`:

| Days Until Start | Phase | Description |
|-----------------|-------|-------------|
| > 14 | `pre_onboarding` | Initial preparation |
| 7-14 | `active_preparation` | Active preparation |
| 0-7 | `immediate_prep` | Final preparation |
| 0 | `day_one` | First day tasks |
| < 0 | `post_start` | Post-start integration |
| All tasks done | `complete` | Onboarding complete |

## Agent Responsibilities

### Coordinator Agent
- Calculates `days_until_start`
- Determines current phase
- Routes to appropriate agents

### IT Agent
- Provisions GitHub access
- Creates Azure AD account
- Sets up development environment

### HR Agent
- Sends welcome email
- Prepares document forms
- Schedules orientation

### Manager Agent
- Notifies manager
- Schedules 1-on-1 meeting
- Prepares team introduction

### Training Agent
- Enrolls in mandatory courses
- Assigns learning paths
- Schedules training sessions

## Error Handling

All tools include comprehensive error handling:

```python
try:
    result = create_onboarding(...)
except ValueError as e:
    # Invalid input data
    print(f"Validation error: {e}")
except Exception as e:
    # Other errors
    print(f"Error: {e}")
```

## Logging

The server logs all operations:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Logs include:
# - Tool invocations
# - Agent executions
# - State transitions
# - Errors and exceptions
```

## Next Steps

1. **Implement Agents**: Complete Phase 2 backend implementation
2. **Database Integration**: Implement Cosmos DB persistence in Phase 3
3. **Add Tools**: Extend with additional tools as needed
4. **Deploy**: Deploy MCP server alongside Azure Functions

## References

- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://modelcontextprotocol.io)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
