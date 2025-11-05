# Azure Developer CLI (azd) Deployment Guide

This project uses Azure Developer CLI (azd) for streamlined provisioning and deployment to Azure.

## Prerequisites

- [Azure Developer CLI](https://aka.ms/azd-install)
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Terraform](https://www.terraform.io/downloads) >= 1.1.7
- An Azure subscription

## Quick Start

### 1. Initialize your environment

```bash
# Login to Azure
az login

# Initialize azd environment (first time only)
azd init

# You'll be prompted to:
# - Name your environment (e.g., "dev", "prod")
# - Select your Azure subscription
# - Select your Azure location
```

### 2. Provision and Deploy

```bash
# Provision infrastructure and deploy all services in one command
azd up
```

This command will:

1. **Provision** infrastructure using Terraform (ACR, Container Apps, AI Foundry, etc.)
2. **Package** your application code (builds Docker images automatically)
3. **Deploy** services to Azure Container Apps and Azure Functions

### 3. Monitor your deployment

```bash
# Open Azure Portal to your resource group
azd show

# View deployment logs
azd monitor

# Get service endpoints
azd env get-values
```

## Individual Commands

### Provision Infrastructure Only

```bash
azd provision
```

Creates all Azure resources defined in the `infra/` folder using Terraform:

- Resource Group
- User-Assigned Managed Identity
- Azure Container Registry (Basic SKU)
- Log Analytics Workspace
- Application Insights
- Azure AI Foundry (Account + Project + GPT-4o deployment)
- Storage Account, Cosmos DB, AI Search (for AI Foundry)
- Container Apps Environment
- Container Apps (backend, ai-service)
- Azure Functions (weather-function)
- Service Plan for Functions

### Build and Deploy Services Only

```bash
# Deploy services (automatically packages/builds Docker images first)
azd deploy
```

The deployment process:

1. **Package stage**: Automatically builds Docker images based on `azure.yaml` configurations
2. **Push**: Pushes images to Azure Container Registry
3. **Deploy**: Updates Container Apps and Functions with new images

> **Note**: The `azd deploy` command automatically runs `azd package` first, which builds and pushes your Docker images. You don't need to manually build or push images.

### Clean Up Resources

```bash
# Delete all Azure resources
azd down
```

## Environment Variables

azd manages environment variables in `.azure/<environment-name>/.env`. Key variables:

- `AZURE_SUBSCRIPTION_ID` - Your Azure subscription
- `AZURE_RESOURCE_GROUP` - Resource group name
- `AZURE_LOCATION` - Azure region (e.g., eastus2)
- `ACR_NAME` - Azure Container Registry name (set after provision)
- `BACKEND_IMAGE` - Backend container image URI
- `AI_SERVICE_IMAGE` - AI service container image URI
- `WEATHER_FUNCTION_IMAGE` - Weather function container image URI

### Viewing Environment Variables

```bash
# List all environment variables
azd env get-values

# Get specific variable
azd env get-value ACR_NAME
```

### Setting Environment Variables

```bash
# Set a variable
azd env set MY_VARIABLE "value"

# Set from Terraform output
azd env set ACR_NAME $(terraform -chdir=./infra output -raw acr_name)
```

## Architecture

The solution deploys:

### Services

- **Backend** (.NET 8 MVC API) → Azure Container App (public ingress)
- **AI Service** (Python FastAPI + Semantic Kernel) → Azure Container App (internal)
- **Weather Function** (Python Azure Function) → Azure Functions (HTTP trigger)

### AI Infrastructure

- **Azure AI Foundry Account** with GPT-4o deployment
- **Azure AI Foundry Project** with connections to:
  - Azure Storage Account
  - Azure Cosmos DB (NoSQL)
  - Azure AI Search

### Supporting Infrastructure

- **Azure Container Registry** for Docker images
- **User-Assigned Managed Identity** for service authentication
- **Log Analytics + Application Insights** for monitoring
- **Azure Functions Service Plan** (Elastic Premium EP1)

## Customization

### Modify Infrastructure

1. Edit Terraform files in `infra/` directory
2. Run `azd provision` to apply changes

### Modify Application Code

1. Edit code in `src/` directory
2. Run `azd deploy` to rebuild and redeploy

### Custom Hooks

The `azure.yaml` file defines hooks that run at different stages:

- `preprovision` - Validates Azure CLI login
- `postprovision` - Retrieves ACR name from Terraform and configures container registry endpoint

You can customize these hooks in `azure.yaml`. Note that Docker image building and pushing is handled automatically by `azd deploy` based on the `docker` configurations in each service definition.

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate to Azure
az login

# Verify subscription
az account show

# Login to ACR
az acr login --name <acr-name>
```

### Image Build Failures

```bash
# Build images locally first to test
docker build -t test -f ./src/backend/Dockerfile ./src
docker build -t test -f ./src/ai-service/Dockerfile ./src/ai-service
docker build -t test -f ./src/weather-function/Dockerfile ./src/weather-function
```

### Terraform State Issues

```bash
# If you need to re-initialize Terraform
cd infra
terraform init -reconfigure
```

### View Deployment Logs

```bash
# Get backend logs
az containerapp logs show -n <backend-name> -g <resource-group>

# Get AI service logs
az containerapp logs show -n <ai-service-name> -g <resource-group>

# Get function logs
az functionapp logs tail -n <function-name> -g <resource-group>
```

## CI/CD Pipeline

To set up CI/CD with GitHub Actions:

```bash
azd pipeline config
```

This will:

1. Create a GitHub Actions workflow
2. Configure Azure credentials as GitHub secrets
3. Enable automated deployment on push to main branch

## Multiple Environments

You can create multiple environments (dev, staging, prod):

```bash
# Create new environment
azd env new staging

# Switch between environments
azd env select dev
azd env select staging

# List environments
azd env list
```

Each environment has its own:

- Azure resources
- Environment variables
- Configuration files in `.azure/<env-name>/`

## Cost Optimization

To minimize costs during development:

1. Use `azd down` when not actively developing
2. Container Apps scale to zero when idle
3. Consider using Free tier for AI Search (update in `infra/modules/ai-storage/main.tf`)
4. Use Basic SKU for ACR (already configured)

## Additional Resources

- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [azd Command Reference](https://learn.microsoft.com/azure/developer/azure-developer-cli/reference)
- [Terraform on Azure](https://learn.microsoft.com/azure/developer/terraform/)
- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
