#!/bin/bash

# Sync .env credentials to local.settings.json for Azure Functions

cd "$(dirname "$0")/../backend"

if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

echo "📝 Loading credentials from .env..."

# Load .env
source .env

# Create local.settings.json with credentials
cat > local.settings.json << EOF
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "",
    "COSMOS_ENDPOINT": "$COSMOS_ENDPOINT",
    "COSMOS_KEY": "$COSMOS_KEY",
    "COSMOS_DATABASE": "$COSMOS_DATABASE",
    "COSMOS_CONTAINER": "$COSMOS_CONTAINER",
    "EMAIL_ENABLED": "$EMAIL_ENABLED",
    "EMAIL_FROM": "$EMAIL_FROM",
    "LOGLEVEL": "$LOGLEVEL"
  },
  "Host": {
    "LocalHttpPort": 7071,
    "CORS": "*",
    "CORSCredentials": false
  }
}
EOF

echo "✅ local.settings.json updated with credentials from .env"
echo ""
echo "Ready to run: func start"
