#!/bin/bash

# HR Onboarding System - Azure Setup Script
# This script automates the creation of Azure resources for the project

set -e  # Exit on error

echo "🚀 HR Onboarding System - Azure Setup"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed${NC}"
    echo "Install it with: brew install azure-cli"
    exit 1
fi

echo -e "${GREEN}✅ Azure CLI found${NC}"

# Check if logged in
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Azure${NC}"
    echo "Running 'az login'..."
    az login
fi

echo -e "${GREEN}✅ Logged in to Azure${NC}"
echo ""

# Get current subscription
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Using subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
echo ""

# Set variables
read -p "Enter resource group name [hr-onboarding-rg]: " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-hr-onboarding-rg}

read -p "Enter location [southeastasia]: " LOCATION
LOCATION=${LOCATION:-southeastasia}

TIMESTAMP=$(date +%s)
COSMOS_ACCOUNT="hr-onboarding-cosmos-${TIMESTAMP}"
FUNCTION_APP="hr-onboarding-func-${TIMESTAMP}"
STORAGE_ACCOUNT="hronboard${TIMESTAMP:0:8}"

echo ""
echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Cosmos DB: $COSMOS_ACCOUNT"
echo "  Function App: $FUNCTION_APP"
echo "  Storage: $STORAGE_ACCOUNT"
echo ""

read -p "Continue with this configuration? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "🏗️  Step 1/6: Creating Resource Group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none

echo -e "${GREEN}✅ Resource Group created${NC}"

echo ""
echo "🗄️  Step 2/6: Creating Cosmos DB (this may take 2-3 minutes)..."
az cosmosdb create \
  --name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --locations regionName="$LOCATION" \
  --kind GlobalDocumentDB \
  --default-consistency-level Session \
  --enable-free-tier true \
  --output none

echo -e "${GREEN}✅ Cosmos DB account created${NC}"

echo ""
echo "📦 Step 3/6: Creating Cosmos DB database and container..."
az cosmosdb sql database create \
  --account-name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --name hr-onboarding \
  --output none

az cosmosdb sql container create \
  --account-name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --database-name hr-onboarding \
  --name onboarding-states \
  --partition-key-path "/new_hire_id" \
  --throughput 400 \
  --output none

echo -e "${GREEN}✅ Database and container created${NC}"

echo ""
echo "🔑 Step 4/6: Retrieving Cosmos DB credentials..."
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query documentEndpoint -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query primaryMasterKey -o tsv)

echo -e "${GREEN}✅ Credentials retrieved${NC}"

echo ""
echo "💾 Step 5/6: Creating Storage Account..."
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --output none

echo -e "${GREEN}✅ Storage account created${NC}"

echo ""
echo "⚡ Step 6/6: Creating Azure Functions App..."
az functionapp create \
  --name "$FUNCTION_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --storage-account "$STORAGE_ACCOUNT" \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux \
  --consumption-plan-location "$LOCATION" \
  --output none

echo -e "${GREEN}✅ Function App created${NC}"

echo ""
echo "⚙️  Configuring Function App settings..."
az functionapp config appsettings set \
  --name "$FUNCTION_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_KEY="$COSMOS_KEY" \
    COSMOS_DATABASE="hr-onboarding" \
    COSMOS_CONTAINER="onboarding-states" \
    EMAIL_ENABLED="false" \
    LOGLEVEL="INFO" \
  --output none

echo -e "${GREEN}✅ Settings configured${NC}"

echo ""
echo "📝 Creating .env file for local development..."
cat > backend/.env << EOF
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

# Logging
LOGLEVEL=INFO
EOF

echo -e "${GREEN}✅ .env file created at backend/.env${NC}"

echo ""
echo "========================================"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo "========================================"
echo ""
echo "📋 Resource Details:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Cosmos DB: $COSMOS_ACCOUNT"
echo "  Function App: $FUNCTION_APP"
echo "  Endpoint: $COSMOS_ENDPOINT"
echo ""
echo "🔑 Credentials saved to: backend/.env"
echo ""
echo "📚 Next Steps:"
echo "  1. Test locally: cd backend && func start"
echo "  2. Deploy: func azure functionapp publish $FUNCTION_APP"
echo "  3. View resources: https://portal.azure.com"
echo ""
echo "💰 Estimated Cost: \$0/month (Free Tier)"
echo ""
echo -e "${YELLOW}⚠️  Important: Keep your .env file secure and never commit it to Git${NC}"
echo ""

# Save resource names for future reference
cat > azure-resources.txt << EOF
Resource Group: $RESOURCE_GROUP
Location: $LOCATION
Cosmos DB Account: $COSMOS_ACCOUNT
Function App: $FUNCTION_APP
Storage Account: $STORAGE_ACCOUNT
Created: $(date)
EOF

echo "Resource names saved to: azure-resources.txt"
echo ""
