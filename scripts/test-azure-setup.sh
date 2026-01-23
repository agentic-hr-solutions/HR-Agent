#!/bin/bash

# Test Azure Setup Script
# Verifies that Azure resources are configured correctly

set -e

echo "🧪 Testing Azure Setup..."
echo "========================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo -e "${RED}❌ backend/.env file not found${NC}"
    echo "Run ./scripts/setup-azure.sh first"
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"

# Load environment variables
source backend/.env

# Test 1: Check Cosmos DB connectivity
echo ""
echo "Test 1: Cosmos DB Connectivity"
echo "------------------------------"

python3 << EOF
import sys
try:
    from azure.cosmos import CosmosClient
    import os
    
    endpoint = "$COSMOS_ENDPOINT"
    key = "$COSMOS_KEY"
    
    if not endpoint or not key:
        print("❌ COSMOS_ENDPOINT or COSMOS_KEY not set")
        sys.exit(1)
    
    client = CosmosClient(endpoint, key)
    database = client.get_database_client("hr-onboarding")
    container = database.get_container_client("onboarding-states")
    
    # Try to query
    items = list(container.query_items(
        query="SELECT VALUE COUNT(1) FROM c",
        enable_cross_partition_query=True
    ))
    
    print("✅ Connected to Cosmos DB successfully")
    print(f"   Records in database: {items[0] if items else 0}")
    
except Exception as e:
    print(f"❌ Cosmos DB connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test 1 Passed${NC}"
else
    echo -e "${RED}❌ Test 1 Failed${NC}"
    exit 1
fi

# Test 2: Check Azure Functions local runtime
echo ""
echo "Test 2: Azure Functions Core Tools"
echo "-----------------------------------"

if ! command -v func &> /dev/null; then
    echo -e "${YELLOW}⚠️  Azure Functions Core Tools not installed${NC}"
    echo "Install with: brew tap azure/functions && brew install azure-functions-core-tools@4"
else
    echo -e "${GREEN}✅ Azure Functions Core Tools installed${NC}"
    func --version
fi

# Test 3: Check Python dependencies
echo ""
echo "Test 3: Python Dependencies"
echo "---------------------------"

cd backend
python3 << EOF
import sys
try:
    import azure.functions
    import langgraph
    import langchain_core
    from azure.cosmos import CosmosClient
    
    print("✅ All required packages installed")
    print(f"   - azure-functions: {azure.functions.__version__}")
    print(f"   - langgraph: {langgraph.__version__}")
    
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install -e '.[dev]'")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test 3 Passed${NC}"
else
    echo -e "${RED}❌ Test 3 Failed${NC}"
    echo "Run: cd backend && pip install -e '.[dev]'"
    exit 1
fi

cd ..

# Test 4: Create test onboarding record
echo ""
echo "Test 4: Create Test Onboarding Record"
echo "-------------------------------------"

python3 << EOF
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, 'backend')

try:
    from integrations.cosmos import OnboardingCosmosClient
    from agents.state import OnboardingState
    
    # Create client
    client = OnboardingCosmosClient()
    
    # Create test state
    test_state: OnboardingState = {
        "new_hire_id": f"test-{int(datetime.now().timestamp())}",
        "new_hire_name": "Test User",
        "email": "test@company.com",
        "role": "Software Engineer",
        "department": "Engineering",
        "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "manager_id": "mgr-test",
        "current_phase": "pre_onboarding",
        "tasks": [],
        "pending_task_ids": [],
        "completed_task_ids": [],
        "failed_task_ids": [],
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Create in Cosmos DB
    result = client.create_state(test_state)
    
    print(f"✅ Created test record: {result['id']}")
    
    # Retrieve it back
    retrieved = client.get_state(result['id'])
    
    if retrieved:
        print(f"✅ Retrieved test record successfully")
        print(f"   Name: {retrieved['new_hire_name']}")
        print(f"   Phase: {retrieved['current_phase']}")
    else:
        print("❌ Failed to retrieve test record")
        sys.exit(1)
    
    # Clean up
    client.delete_state(result['id'])
    print(f"✅ Deleted test record")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test 4 Passed${NC}"
else
    echo -e "${RED}❌ Test 4 Failed${NC}"
    exit 1
fi

# Test 5: Check Function App deployment readiness
echo ""
echo "Test 5: Deployment Readiness"
echo "----------------------------"

REQUIRED_FILES=(
    "backend/function_app.py"
    "backend/host.json"
    "backend/pyproject.toml"
    "backend/.env"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo -e "${RED}❌ $file not found${NC}"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = true ]; then
    echo -e "${GREEN}✅ Test 5 Passed${NC}"
else
    echo -e "${RED}❌ Test 5 Failed${NC}"
    exit 1
fi

# Summary
echo ""
echo "========================================"
echo -e "${GREEN}✅ All Tests Passed!${NC}"
echo "========================================"
echo ""
echo "Your Azure setup is ready! 🎉"
echo ""
echo "Next steps:"
echo "  1. Start local development:"
echo "     cd backend && func start"
echo ""
echo "  2. Test the API:"
echo "     curl -X POST http://localhost:7071/api/onboarding/create \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"name\":\"Test\",\"role\":\"Engineer\",\"start_date\":\"2026-02-01\"}'"
echo ""
echo "  3. Deploy to Azure:"
echo "     func azure functionapp publish <FUNCTION_APP_NAME>"
echo ""
