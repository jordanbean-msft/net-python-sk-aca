# Infrastructure Deployment

This directory contains Terraform configuration for deploying the multi-container chat application to Azure Container Apps.

## Architecture

The infrastructure deploys:

- **Azure Container Apps Environment** - Hosting platform for containerized applications
- **Three Container Apps**:
  - **Backend** (C# .NET 8 API) - Serves React frontend and proxies to AI service (external ingress)
  - **AI Service** (Python FastAPI + Semantic Kernel) - AI chat completion with tool calling (internal ingress)
  - **Weather Function** (Python Azure Function) - Weather data tool for AI agent (internal ingress)
- **Azure Container Registry** - Private container image storage
- **User-Assigned Managed Identity** - For ACR pull and Azure AI authentication
- **Log Analytics Workspace** - Centralized logging
- **Application Insights** - Application monitoring and telemetry

## Prerequisites

1. **Azure Subscription** with appropriate permissions
2. **Terraform** >= 1.10.0
3. **Azure CLI** installed and logged in (`az login`)
4. **Azure AI Foundry Project** already created with a model deployment

## Quick Start

### 1. Configure Variables

Copy the example file and edit with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Required variables:

- `subscription_id` - Your Azure subscription ID
- `resource_group_name` - Name for the resource group
- `location` - Azure region (e.g., "eastus")
- `azure_ai_project_endpoint` - Your AI Foundry project endpoint
- `azure_ai_model_deployment` - Model deployment name (default: "gpt-4o")

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Deploy Infrastructure

```bash
terraform plan
terraform apply
```

### 4. Build and Push Container Images

After infrastructure is deployed, build and push your container images:

```bash
# Get ACR details
ACR_NAME=$(terraform output -raw acr_name)
ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)

# Login to ACR
az acr login --name $ACR_NAME

# Build and push from project root
cd ..

# Backend
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/backend:latest \
  -f src/backend/Dockerfile \
  --build-arg BUILD_ENV=production \
  --build-arg PORT=8080 \
  src
docker push $ACR_LOGIN_SERVER/backend:latest

# AI Service
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/ai-service:latest \
  -f src/ai-service/Dockerfile \
  --build-arg PORT=8000 \
  src/ai-service
docker push $ACR_LOGIN_SERVER/ai-service:latest

# Weather Function
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/weather-function:latest \
  -f src/weather-function/Dockerfile \
  src/weather-function
docker push $ACR_LOGIN_SERVER/weather-function:latest
```

### 5. Update Container Apps with New Images

Update `terraform.tfvars` with the image names:

```hcl
backend_image          = "acr<suffix>.azurecr.io/backend:latest"
ai_service_image       = "acr<suffix>.azurecr.io/ai-service:latest"
weather_function_image = "acr<suffix>.azurecr.io/weather-function:latest"
```

Apply the changes:

```bash
terraform apply
```

### 6. Access the Application

Get the backend URL:

```bash
terraform output backend_url
```

Open the URL in your browser to access the chat application.

## Configuration

### Environment Variables

Container apps are configured with environment variables for:

**Backend:**

- `PORT` - HTTP port (8080)
- `ASPNETCORE_ENVIRONMENT` - Environment name
- `Logging__LogLevel__Default` - Log level
- `PythonApiUrl` - Internal URL to AI service

**AI Service:**

- `PORT` - HTTP port (8000)
- `LOG_LEVEL` - Log level (info/debug)
- `AZURE_AI_PROJECT_ENDPOINT` - AI Foundry endpoint
- `AZURE_AI_MODEL_DEPLOYMENT` - Model deployment name
- `AZURE_OPENAI_API_KEY` - Optional API key (uses managed identity if not set)
- `WeatherFunctionUrl` - Internal URL to weather function
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - App Insights connection
- `AZURE_CLIENT_ID` - Managed identity client ID

**Weather Function:**

- `PYTHONUNBUFFERED` - Python unbuffered output
- `AzureFunctionsJobHost__logging__logLevel__*` - Function logging configuration
- `AzureFunctionsJobHost__Logging__Console__IsEnabled` - Console logging

### Scaling

Container apps are configured with:

- **Minimum replicas**: 1
- **Maximum replicas**: 3-10 depending on service

### Managed Identity

The user-assigned managed identity is used for:

- Pulling images from Azure Container Registry (AcrPull role)
- Authenticating to Azure AI Foundry (if not using API key)

## Outputs

Key outputs after deployment:

```bash
# Application URLs
terraform output backend_url

# Container Registry
terraform output acr_login_server
terraform output acr_name

# Managed Identity
terraform output managed_identity_client_id
terraform output managed_identity_principal_id

# Monitoring
terraform output log_analytics_workspace_id
terraform output application_insights_connection_string
```

## Diagnostic Logging

When `enable_diagnostics = true` (default), Container App Environment logs are sent to Log Analytics:

- Container console logs
- System logs
- Metrics

## Clean Up

To destroy all resources:

```bash
terraform destroy
```

## Troubleshooting

### Container Apps Not Starting

Check logs:

```bash
az containerapp logs show \
  --name ca-backend-<suffix> \
  --resource-group <rg-name> \
  --follow
```

### Image Pull Failures

Verify managed identity has AcrPull permission:

```bash
az role assignment list \
  --assignee <managed-identity-principal-id> \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.ContainerRegistry/registries/<acr-name>
```

### AI Service Connection Issues

Verify:

1. `AZURE_AI_PROJECT_ENDPOINT` is correct
2. Managed identity has appropriate permissions on AI Foundry
3. Model deployment name matches

## Architecture Notes

- All container apps use the same Container App Environment
- Backend has **external ingress** (public HTTPS)
- AI Service and Weather Function have **internal ingress** (accessible only within environment)
- No VNet integration (simplified for development)
- Uses managed identity for authentication where possible
