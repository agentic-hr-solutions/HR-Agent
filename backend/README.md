# HR Onboarding API

Azure Functions-based API for the Employee Onboarding Agentic AI system.

## Endpoints

### POST /api/onboarding/create
Create a new onboarding workflow.

**Request:**
```json
{
  "name": "John Doe",
  "role": "Software Engineer",
  "start_date": "2026-02-15",
  "department": "Engineering",
  "manager_id": "mgr-001"
}
```

**Response (201):**
```json
{
  "new_hire_id": "nh-1234567890",
  "new_hire_name": "John Doe",
  "email": "john.doe@company.com",
  "role": "Software Engineer",
  "department": "Engineering",
  "start_date": "2026-02-15",
  "manager_id": "mgr-001",
  "current_phase": "pre_onboarding",
  "tasks": [...],
  "completed_tasks": ["hr-001", "hr-002", ...],
  "pending_tasks": [],
  "messages": ["[Coordinator] New hire John Doe is 24 days from start date..."],
  "created_at": "2026-01-22T10:00:00",
  "updated_at": "2026-01-22T10:00:05",
  "errors": []
}
```

### GET /api/onboarding/{id}
Retrieve onboarding status by ID.

**Response (200):**
```json
{
  "new_hire_id": "nh-1234567890",
  "new_hire_name": "John Doe",
  "current_phase": "active_preparation",
  ...
}
```

### PUT /api/onboarding/{id}/advance
Advance onboarding workflow to next phase.

### GET /api/onboarding/{id}/status
Get quick status summary.

### GET /api/health
Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "hr-onboarding-api",
  "timestamp": "2026-01-22T10:00:00"
}
```

## Local Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
```

### Run Locally
```bash
# Start Azure Functions runtime
func start

# API will be available at http://localhost:7071
```

### Test Endpoints
```bash
# Health check
curl http://localhost:7071/api/health

# Create onboarding
curl -X POST http://localhost:7071/api/onboarding/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "role": "Engineer",
    "start_date": "2026-03-01"
  }'
```

## Deployment

### Azure Functions Deployment
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-hr-onboarding --location eastus

# Create storage account
az storage account create \
  --name sthrონბოarding \
  --resource-group rg-hr-onboarding \
  --location eastus

# Create function app
az functionapp create \
  --resource-group rg-hr-onboarding \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name func-hr-onboarding \
  --storage-account sthrონბოarding

# Deploy
func azure functionapp publish func-hr-onboarding
```

### Environment Variables
Set these in Azure Portal or via CLI:
```bash
az functionapp config appsettings set \
  --name func-hr-onboarding \
  --resource-group rg-hr-onboarding \
  --settings \
    COSMOS_ENDPOINT="https://your-account.documents.azure.com:443/" \
    COSMOS_KEY="your-key" \
    EMAIL_ENABLED="true"
```

## Architecture

```
┌─────────────────┐
│  Azure Function │
│   (function_app)│
└────────┬────────┘
         │
         ├──> LangGraph Workflow
         │    └──> 5 Agents (Coordinator, IT, HR, Manager, Training)
         │
         ├──> Cosmos DB (state persistence)
         │
         └──> Email Service (notifications)
```

## Workflow Phases

1. **pre_onboarding** (>14 days before start)
   - HR tasks: offer letter, documents, background check

2. **active_preparation** (7-14 days)
   - IT provisioning: email, laptop, accounts

3. **immediate_prep** (0-7 days)
   - Manager tasks: 1:1 scheduling, mentor assignment

4. **post_start** (after start date)
   - Training: orientation, LMS access, courses

## Task Categories

- **IT Tasks** (5): Email, laptop, badge, software, VPN
- **HR Tasks** (5): Offer, documents, background, payroll, benefits
- **Manager Tasks** (5): 1:1, mentor, 30-60-90 plan, schedule, team intro
- **Training Tasks** (5): Mandatory training, orientation, LMS, compliance, learning path

**Total**: 20 automated tasks per onboarding

## CORS Configuration

API supports CORS for frontend integration:
- Allowed origins: `*` (configure for production)
- Allowed methods: GET, POST, PUT, OPTIONS
- Allowed headers: Content-Type, Authorization

## Error Handling

All endpoints return JSON error responses:

```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

Status codes:
- `400`: Bad request (missing fields, validation errors)
- `404`: Resource not found
- `500`: Internal server error
- `501`: Not implemented (Cosmos DB features pending)

## Testing

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## License

Internal use only.
