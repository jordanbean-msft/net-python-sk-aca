# Azure Deployment Workflow

This guide walks through deploying the multi-container chat application to Azure using Terraform.

## Prerequisites

- Azure subscription with Owner or Contributor permissions
- Azure CLI installed and authenticated (`az login`)
- Terraform >= 1.10.0 installed
- Docker with buildx support (for multi-platform builds)
- **Azure AI Foundry project already created** with a GPT-4o model deployment

## Architecture Overview

The Terraform configuration deploys:

```
┌─────────────────────────────────────────────────────┐
│         Azure Container Apps Environment            │
│                                                      │
│  ┌──────────────┐   ┌───────────────┐              │
│  │   Backend    │───│  AI Service   │              │
│  │  (External)  │   │  (Internal)   │              │
│  └──────────────┘   └───────┬───────┘              │
│                             │                       │
│                      ┌──────▼────────┐              │
│                      │    Weather    │              │
│                      │   Function    │              │
│                      │  (Internal)   │              │
│                      └───────────────┘              │
│                                                      │
└─────────────────────────────────────────────────────┘
         │                    │
         │                    │
    ┌────▼────┐          ┌────▼────────────────┐
    │   ACR   │          │  Application        │
    └─────────┘          │  Insights           │
                         └─────────────────────┘
```

**Resources:**

- Container Apps Environment (shared hosting platform)
- 3 Container Apps: backend (public), ai-service (internal), weather-function (internal)
- Azure Container Registry (private image storage)
- User-Assigned Managed Identity (ACR pull + AI auth)
- Log Analytics Workspace
- Application Insights

## Step 1: Configure Terraform Variables

1. Navigate to the `infra` directory:

   ```bash
   cd infra
   ```

2. Copy the example variables file:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. Edit `terraform.tfvars` with your Azure details:

   ```hcl
   subscription_id     = "your-subscription-id"
   resource_group_name = "rg-chat-app"
   location            = "eastus"

   # Your AI Foundry project endpoint
   azure_ai_project_endpoint = "https://your-ai-account.services.ai.azure.com/api/projects/your-project"
   azure_ai_model_deployment = "gpt-4o"

   # Optional: API key (if not using managed identity)
   # azure_openai_api_key = "your-api-key"
   ```

4. Save the file.

## Step 2: Deploy Infrastructure

1. Initialize Terraform:

   ```bash
   terraform init
   ```

2. Review the deployment plan:

   ```bash
   terraform plan
   ```

3. Deploy the infrastructure:

   ```bash
   terraform apply
   ```

   Type `yes` when prompted to confirm.

4. Wait for deployment to complete (~5-10 minutes).

5. Note the outputs:
   ```bash
   terraform output
   ```

## Step 3: Build and Push Container Images

Use the provided script to build and push all container images:

```bash
./deploy-images.sh
```

This script will:

1. Retrieve ACR details from Terraform outputs
2. Login to Azure Container Registry
3. Build all three container images for linux/amd64 platform
4. Push images to ACR

**Manual alternative:**

```bash
# Get ACR details
ACR_NAME=$(terraform output -raw acr_name)
ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)

# Login
az acr login --name $ACR_NAME

# Build and push (from project root)
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

## Step 4: Update Container Apps with Images

1. Edit `terraform.tfvars` to add the image names:

   ```hcl
   backend_image          = "acr<suffix>.azurecr.io/backend:latest"
   ai_service_image       = "acr<suffix>.azurecr.io/ai-service:latest"
   weather_function_image = "acr<suffix>.azurecr.io/weather-function:latest"
   ```

2. Apply the configuration:
   ```bash
   terraform apply
   ```

## Step 5: Access the Application

Get the application URL:

```bash
terraform output backend_url
```

Open the URL in your browser to access the chat application.

## Monitoring and Troubleshooting

### View Application Logs

**Backend logs:**

```bash
az containerapp logs show \
  --name ca-backend-$(terraform output -raw unique_suffix) \
  --resource-group $(terraform output -raw resource_group_name) \
  --follow
```

**AI Service logs:**

```bash
az containerapp logs show \
  --name ca-ai-service-$(terraform output -raw unique_suffix) \
  --resource-group $(terraform output -raw resource_group_name) \
  --follow
```

**Weather Function logs:**

```bash
az containerapp logs show \
  --name ca-weather-$(terraform output -raw unique_suffix) \
  --resource-group $(terraform output -raw resource_group_name) \
  --follow
```

### View in Azure Portal

1. Navigate to the resource group in Azure Portal
2. Select the Container App Environment
3. View individual container apps and their logs

### Application Insights

View telemetry and traces:

```bash
APPINSIGHTS_NAME="appi-$(terraform output -raw unique_suffix)"
az monitor app-insights component show \
  --app $APPINSIGHTS_NAME \
  --resource-group $(terraform output -raw resource_group_name)
```

### Common Issues

**Container not starting:**

- Check logs with `az containerapp logs show`
- Verify image was pushed successfully to ACR
- Check managed identity has AcrPull permissions

**AI Service connection issues:**

- Verify `AZURE_AI_PROJECT_ENDPOINT` is correct
- Check model deployment name matches
- Verify managed identity permissions on AI Foundry

**Weather Function not responding:**

- Check internal ingress configuration
- Verify Azure Functions runtime is starting correctly

## Updating the Application

To deploy code changes:

1. Rebuild and push images:

   ```bash
   ./deploy-images.sh
   ```

2. Restart container apps to pull new images:

   ```bash
   az containerapp revision restart \
     --name ca-backend-$(terraform output -raw unique_suffix) \
     --resource-group $(terraform output -raw resource_group_name)

   az containerapp revision restart \
     --name ca-ai-service-$(terraform output -raw unique_suffix) \
     --resource-group $(terraform output -raw resource_group_name)

   az containerapp revision restart \
     --name ca-weather-$(terraform output -raw unique_suffix) \
     --resource-group $(terraform output -raw resource_group_name)
   ```

## Scaling Configuration

Container apps are configured with auto-scaling:

- **Backend & AI Service**: 1-10 replicas
- **Weather Function**: 1-3 replicas

Modify in `main.tf`:

```hcl
template {
  min_replicas = 1
  max_replicas = 10
  # ...
}
```

## Cost Management

To minimize costs:

1. Use Basic SKU for ACR (already configured)
2. Keep min_replicas at 1 for dev environments
3. Delete resources when not in use:
   ```bash
   terraform destroy
   ```

## Security Considerations

**Managed Identity:**

- Used for ACR pull authentication
- Used for Azure AI Foundry authentication (if API key not provided)
- Reduces secret management

**Network Security:**

- Backend has external ingress (HTTPS with automatic TLS)
- AI Service and Weather Function use internal ingress only
- No VNet integration (simplified for dev)

**Secrets:**

- API keys stored in Container App secrets
- Never commit `terraform.tfvars` to version control

## CI/CD Integration

For automated deployments, consider:

1. **GitHub Actions workflow:**

   - Trigger on push to main branch
   - Build and push Docker images
   - Run `terraform apply`
   - Deploy new container app revisions

2. **Azure DevOps pipeline:**
   - Use Terraform tasks
   - Store state in Azure Storage backend
   - Use service principal for authentication

## Cleanup

To delete all resources:

```bash
terraform destroy
```

Type `yes` when prompted.

**Note:** This will delete:

- All container apps
- Container App Environment
- Azure Container Registry (including all images)
- Log Analytics Workspace
- Application Insights
- Managed Identity
- Resource Group

## Next Steps

- Configure custom domain for backend
- Add authentication/authorization
- Implement CI/CD pipeline
- Add VNet integration for production
- Configure Azure Front Door for global distribution
- Set up alerts and monitoring
