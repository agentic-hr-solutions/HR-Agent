#!/bin/bash

# HR Onboarding System - Azure Setup Script (Non-Interactive)
# Uses default values for quick setup

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 HR Onboarding System - Quick Azure Setup"
echo "==========================================="
echo ""

# Default configuration
RESOURCE_GROUP="hr-onboarding-rg"
LOCATION="southeastasia"
TIMESTAMP=$(date +%s)
COSMOS_ACCOUNT="hr-cosmos-${TIMESTAMP}"
FUNCTION_APP="hr-func-${TIMESTAMP}"
STORAGE_ACCOUNT="hronboard${TIMESTAMP:0:8}"

echo "Using default configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Cosmos DB: $COSMOS_ACCOUNT"
echo "  Function App: $FUNCTION_APP"
echo ""

# Create resource group
echo "📦 Creating Resource Group..."
if az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Resource group already exists, using existing${NC}"
else
    az group create \
      --name "$RESOURCE_GROUP" \
      --location "$LOCATION" \
      --output none
    echo -e "${GREEN}✅ Resource Group created${NC}"
fi

# Create Cosmos DB
echo ""
echo "🗄️  Creating Cosmos DB (2-3 minutes)..."
if az cosmosdb show --name "$COSMOS_ACCOUNT" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Cosmos DB already exists${NC}"
else
    az cosmosdb create \
      --name "$COSMOS_ACCOUNT" \
      --resource-group "$RESOURCE_GROUP" \
      --locations regionName="$LOCATION" \
      --kind GlobalDocumentDB \
      --default-consistency-level Session \
      --enable-free-tier true \
      --output none
    echo -e "${GREEN}✅ Cosmos DB created${NC}"
fi

# Create database and container
echo ""
echo "📊 Creating database and container..."
az cosmosdb sql database create \
  --account-name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --name hr-onboarding \
  --output none 2>/dev/null || echo "Database already exists"

az cosmosdb sql container create \
  --account-name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --database-name hr-onboarding \
  --name onboarding-states \
  --partition-key-path "/new_hire_id" \
  --throughput 400 \
  --output none 2>/dev/null || echo "Container already exists"

echo -e "${GREEN}✅ Database configured${NC}"

# Get credentials
echo ""
echo "🔑 Getting Cosmos DB credentials..."
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query documentEndpoint -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query primaryMasterKey -o tsv)

echo -e "${GREEN}✅ Credentials retrieved${NC}"

# Create storage account
echo ""
echo "💾 Creating Storage Account..."
if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Storage account already exists${NC}"
else
    az storage account create \
      --name "$STORAGE_ACCOUNT" \
      --resource-group "$RESOURCE_GROUP" \
      --location "$LOCATION" \
      --sku Standard_LRS \
      --output none
    echo -e "${GREEN}✅ Storage account created${NC}"
fi

# Create Function App
echo ""
echo "⚡ Creating Azure Functions App..."
if az functionapp show --name "$FUNCTION_APP" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Function App already exists${NC}"
else
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
fi

# Configure app settings
echo ""
echo "⚙️  Configuring Function App..."
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

echo -e "${GREEN}✅ Function App configured${NC}"

# Create .env file
echo ""
echo "📝 Creating .env file..."
mkdir -p backend
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

echo -e "${GREEN}✅ .env file created${NC}"

# Save resource info
cat > azure-resources.txt << EOF
Resource Group: $RESOURCE_GROUP
Location: $LOCATION
Cosmos DB Account: $COSMOS_ACCOUNT
Function App: $FUNCTION_APP
Storage Account: $STORAGE_ACCOUNT
Cosmos Endpoint: $COSMOS_ENDPOINT
Created: $(date)
EOF

# Final summary
echo ""
echo "========================================"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo "========================================"
echo ""
echo "📋 Resources Created:"
echo "  • Resource Group: $RESOURCE_GROUP"
echo "  • Cosmos DB: $COSMOS_ACCOUNT"
echo "  • Function App: $FUNCTION_APP"
echo "  • Storage: $STORAGE_ACCOUNT"
echo ""
echo "📁 Files Created:"
echo "  • backend/.env (credentials)"
echo "  • azure-resources.txt (resource names)"
echo ""
echo "🔑 Important: Your .env file contains secrets!"
echo "   → Never commit it to Git"
echo "   → It's already in .gitignore"
echo ""
echo "📚 Next Steps:"
echo ""
echo "  1️⃣  Install dependencies:"
echo "     cd backend && pip install -e '.[dev]'"
echo ""
echo "  2️⃣  Test the setup:"
echo "     ./scripts/test-azure-setup.sh"
echo ""
echo "  3️⃣  Start local development:"
echo "     cd backend && func start"
echo ""
echo "  4️⃣  Deploy to Azure:"
echo "     func azure functionapp publish $FUNCTION_APP"
echo ""
echo "💰 Cost: \$0/month (Free Tier)"
echo ""
echo "🌐 View in Azure Portal:"
echo "   https://portal.azure.com/#@/resource/subscriptions/.../resourceGroups/$RESOURCE_GROUP"
echo ""
