#!/bin/bash

# Azure Functions Deployment Script for Cloud Food Order Platform
# Run this from the clood_project/ directory
# Functions: getmeal, registermeal, submitorder

set -e

echo "🚀 Azure Functions Deployment Script"
echo "===================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if Functions Core Tools is installed
if ! command -v func &> /dev/null; then
    echo "❌ Azure Functions Core Tools not found. Please install:"
    echo "   npm install -g azure-functions-core-tools@4"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Configuration
RESOURCE_GROUP="CC_M_B_G6"
LOCATION="westeurope"  # Change to your preferred location
FUNCTION_APP_NAME="clood-functions-$(date +%s | tail -c 4)"
STORAGE_ACCOUNT="1sttry"
PYTHON_VERSION="3.11"

echo ""
echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   Function App: $FUNCTION_APP_NAME"
echo "   Storage Account: $STORAGE_ACCOUNT"
echo "   Python Version: $PYTHON_VERSION"
echo ""
echo "📡 Azure Functions to Deploy:"
echo "   - getmeal (GET /api/meals)"
echo "   - registermeal (POST /api/registerMeal)"
echo "   - submitorder (POST /api/submitOrder)"
echo ""

# Check if logged into Azure
echo "🔐 Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "   Please log in to Azure..."
    az login
fi

# Create Resource Group
echo "📦 Creating Resource Group..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    az group create --name $RESOURCE_GROUP --location $LOCATION
    print_status "Resource group created: $RESOURCE_GROUP"
else
    print_warning "Resource group already exists: $RESOURCE_GROUP"
fi

# Create Storage Account
echo "💾 Creating Storage Account..."
if ! az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP &> /dev/null; then
    az storage account create \
        --name $STORAGE_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2
    print_status "Storage account created: $STORAGE_ACCOUNT"
else
    print_warning "Storage account already exists: $STORAGE_ACCOUNT"
fi

# Create Function App
echo "⚡ Creating Function App..."
if ! az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    az functionapp create \
        --resource-group $RESOURCE_GROUP \
        --consumption-plan-location $LOCATION \
        --runtime python \
        --runtime-version $PYTHON_VERSION \
        --functions-version 4 \
        --name $FUNCTION_APP_NAME \
        --storage-account $STORAGE_ACCOUNT \
        --os-type Linux
    print_status "Function app created: $FUNCTION_APP_NAME"
else
    print_warning "Function app already exists: $FUNCTION_APP_NAME"
fi

# Get storage connection string
echo "🔗 Getting storage connection string..."
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query connectionString \
    --output tsv)

# Configure Function App settings
echo "⚙️ Configuring Function App..."
az functionapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $FUNCTION_APP_NAME \
    --settings \
        AzureWebJobsStorage=$STORAGE_CONNECTION_STRING \
        AzureStorageConnectionString=$STORAGE_CONNECTION_STRING \
        FUNCTIONS_WORKER_RUNTIME=python \
        PYTHON_ENABLE_WORKER_EXTENSIONS=1 \
        PYTHON_ISOLATE_WORKER_DEPENDENCIES=1

# Configure CORS
echo "🌐 Configuring CORS..."
az functionapp cors add \
    --resource-group $RESOURCE_GROUP \
    --name $FUNCTION_APP_NAME \
    --allowed-origins "*"  # For development only. Change for production!

print_status "CORS configured to allow all origins (development only)"

# Deploy the functions
echo "🚀 Deploying functions..."
func azure functionapp publish $FUNCTION_APP_NAME --python

# Get the function URL
echo "🔗 Getting function URLs..."
FUNCTION_URL=$(az functionapp show \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "defaultHostName" \
    --output tsv)

echo ""
echo "===================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "===================================="
echo ""
echo "📋 Your Azure Functions are now live!"
echo ""
echo "🔗 Function App URL:"
echo "   https://$FUNCTION_URL"
echo ""
echo "📡 API Endpoints:"
echo "   GET  https://$FUNCTION_URL/api/meals?area=Central"
echo "   POST https://$FUNCTION_URL/api/registerMeal"
echo "   POST https://$FUNCTION_URL/api/submitOrder"
echo ""
echo "🔑 Connection String (save this for frontend):"
echo "   $STORAGE_CONNECTION_STRING"
echo ""
echo "📝 Next Steps:"
echo "   1. Test your functions with the URLs above"
echo "   2. Update your frontend JavaScript with the API base URL:"
echo "      const API_BASE_URL = 'https://$FUNCTION_URL/api'"
echo "   3. Run the test script to verify everything works"
echo ""
echo "🧪 To test locally first:"
echo "   1. Copy local.settings.json.example to local.settings.json"
echo "   2. Add your Azure Storage connection string to local.settings.json"
echo "   3. Run: func start"
echo "   4. Test endpoints at: http://localhost:7071/api/"
echo "      - http://localhost:7071/api/meals?area=Central"
echo "      - http://localhost:7071/api/registerMeal (POST)"
echo "      - http://localhost:7071/api/submitOrder (POST)"
echo ""
echo "🧪 To test the deployed functions:"
echo "   python testdeploy.py https://$FUNCTION_URL/api"
echo ""
echo "✅ All done! Your serverless backend is ready."