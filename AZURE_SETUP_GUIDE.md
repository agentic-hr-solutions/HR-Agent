# 🚀 Azure Setup Guide - HR Onboarding System

## Prerequisites

- Azure account (Free trial works: https://azure.microsoft.com/free)
- Azure CLI installed
- VS Code with Azure extensions

## Quick Setup (5 Minutes)

### 1. Install Azure CLI (if not installed)

```bash
# macOS
brew update && brew install azure-cli

# Verify installation
az --version
```

### 2. Login to Azure

```bash
az login
```

### 3. Run Automated Setup Script

```bash
chmod +x scripts/setup-azure.sh
./scripts/setup-azure.sh
```

This script will:
- ✅ Create Resource Group
- ✅ Create Cosmos DB account
- ✅ Create database and container
- ✅ Create Azure Functions app
- ✅ Generate `.env` file with credentials

---

## Manual Setup (Step-by-Step)

### Step 1: Set Variables

```bash
# Set your preferences
RESOURCE_GROUP="hr-onboarding-rg"
LOCATION="southeastasia"  # or "eastus"
COSMOS_ACCOUNT="hr-onboarding-cosmos-$(date +%s)"
FUNCTION_APP="hr-onboarding-func-$(date +%s)"
STORAGE_ACCOUNT="hronboarding$(date +%s | cut -c 1-8)"
```

### Step 2: Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 3: Create Cosmos DB (Free Tier)

```bash
# Create Cosmos DB account
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --locations regionName=$LOCATION \
  --kind GlobalDocumentDB \
  --default-consistency-level Session \
  --enable-free-tier true

# Create database
az cosmosdb sql database create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --name hr-onboarding

# Create container with partition key
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --database-name hr-onboarding \
  --name onboarding-states \
  --partition-key-path "/new_hire_id" \
  --throughput 400

# Get Cosmos DB connection details
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query documentEndpoint -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query primaryMasterKey -o tsv)

echo "Cosmos Endpoint: $COSMOS_ENDPOINT"
echo "Cosmos Key: $COSMOS_KEY"
```

### Step 4: Create Storage Account (for Azure Functions)

```bash
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS
```

### Step 5: Create Azure Functions App

```bash
az functionapp create \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --storage-account $STORAGE_ACCOUNT \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux \
  --consumption-plan-location $LOCATION
```

### Step 6: Configure Function App Settings

```bash
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_KEY="$COSMOS_KEY" \
    COSMOS_DATABASE="hr-onboarding" \
    COSMOS_CONTAINER="onboarding-states" \
    EMAIL_ENABLED="false" \
    LOGLEVEL="INFO"
```

---

## Local Development Setup

### 1. Create `.env` file

```bash
cd backend
cp .env.example .env
```

### 2. Fill in `.env` with Azure credentials

```bash
# Use the output from Azure CLI commands above
cat > .env << EOF
# Azure Cosmos DB Configuration
COSMOS_ENDPOINT=$COSMOS_ENDPOINT
COSMOS_KEY=$COSMOS_KEY
COSMOS_DATABASE=hr-onboarding
COSMOS_CONTAINER=onboarding-states

# Email Service Configuration
EMAIL_ENABLED=false
EMAIL_FROM=noreply@company.com

# Azure Functions Configuration
FUNCTIONS_WORKER_RUNTIME=python
AzureWebJobsStorage=UseDevelopmentStorage=true

# Logging
LOGLEVEL=INFO
EOF
```

### 3. Install Dependencies

```bash
cd backend
pip install -e ".[dev]"
```

### 4. Test Local Functions

```bash
# Install Azure Functions Core Tools
brew tap azure/functions
brew install azure-functions-core-tools@4

# Start local server
func start
```

Expected output:
```
Functions:
  create_onboarding: [POST] http://localhost:7071/api/onboarding/create
  get_onboarding: [GET] http://localhost:7071/api/onboarding/{id}
  update_task: [PUT] http://localhost:7071/api/onboarding/{id}/task/{task_id}
```

---

## Testing the Setup

### Test 1: Create Onboarding

```bash
curl -X POST http://localhost:7071/api/onboarding/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nguyen Van A",
    "role": "Software Engineer",
    "department": "Engineering",
    "start_date": "2026-02-01",
    "manager_id": "mgr-001"
  }'
```

Expected response:
```json
{
  "status": "success",
  "onboarding_id": "nh-...",
  "message": "Onboarding workflow started",
  "state": {
    "new_hire_name": "Nguyen Van A",
    "current_phase": "pre_onboarding",
    "tasks": [...]
  }
}
```

### Test 2: Get Onboarding Status

```bash
curl http://localhost:7071/api/onboarding/{onboarding_id}
```

### Test 3: Cosmos DB Direct Query

```bash
# Install Cosmos DB Python SDK test
python << EOF
from azure.cosmos import CosmosClient
import os

client = CosmosClient("$COSMOS_ENDPOINT", "$COSMOS_KEY")
database = client.get_database_client("hr-onboarding")
container = database.get_container_client("onboarding-states")

# List all items
items = list(container.query_items(
    query="SELECT * FROM c",
    enable_cross_partition_query=True
))

print(f"Found {len(items)} onboarding records")
for item in items:
    print(f"- {item['new_hire_name']} ({item['current_phase']})")
EOF
```

---

## Deployment to Azure

### Option 1: Using Azure CLI

```bash
cd backend

# Create deployment package
pip install --target=".python_packages/lib/site-packages" -r requirements.txt

# Deploy
func azure functionapp publish $FUNCTION_APP
```

### Option 2: Using VS Code

1. Install "Azure Functions" extension
2. Click Azure icon in sidebar
3. Sign in to Azure
4. Right-click Function App → Deploy to Function App
5. Select `backend` folder

---

## Verify Deployment

```bash
# Get Function App URL
FUNCTION_URL=$(az functionapp show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query defaultHostName -o tsv)

echo "Function URL: https://$FUNCTION_URL"

# Test deployed endpoint
curl -X POST https://$FUNCTION_URL/api/onboarding/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "role": "Engineer",
    "start_date": "2026-02-01"
  }'
```

---

## Cost Estimation (Free Tier)

| Resource | Free Tier | Expected Usage | Cost |
|----------|-----------|----------------|------|
| Cosmos DB | 1000 RU/s, 25GB | 400 RU/s, <1GB | **$0** |
| Azure Functions | 1M executions | <10K/month | **$0** |
| Storage | 5GB | <100MB | **$0** |
| **Total** | | | **$0/month** |

---

## Troubleshooting

### Issue 1: "Cosmos DB not found"

```bash
# Check if Cosmos DB is ready
az cosmosdb show --name $COSMOS_ACCOUNT --resource-group $RESOURCE_GROUP

# Wait 2-3 minutes for provisioning to complete
```

### Issue 2: "Function App deployment failed"

```bash
# Check logs
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# Restart function app
az functionapp restart --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

### Issue 3: "CORS error from frontend"

```bash
# Enable CORS for all origins (dev only)
az functionapp cors add \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins '*'
```

---

## Cleanup (Delete All Resources)

```bash
# Delete entire resource group
az group delete --name $RESOURCE_GROUP --yes --no-wait

# This deletes:
# - Cosmos DB
# - Azure Functions
# - Storage Account
# - All data
```

---

## Next Steps

- ✅ Setup complete? → Test with frontend (Phase 3)
- ✅ Deploy to production? → Follow deployment guide
- ✅ Add monitoring? → Setup Application Insights

## Support

- Azure Free Tier: https://azure.microsoft.com/free
- Cosmos DB Docs: https://learn.microsoft.com/azure/cosmos-db/
- Azure Functions Docs: https://learn.microsoft.com/azure/azure-functions/
