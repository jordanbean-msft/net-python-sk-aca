output "AZURE_LOCATION" {
  description = "Azure region where resources are deployed"
  value       = var.location
}

output "AZURE_RESOURCE_GROUP" {
  description = "Name of the resource group"
  value       = var.resource_group_name
}

output "AZURE_CONTAINER_REGISTRY_ENDPOINT" {
  description = "Login server for Azure Container Registry"
  value       = module.acr.login_server
}

output "AZURE_CONTAINER_REGISTRY_NAME" {
  description = "Name of the Azure Container Registry"
  value       = module.acr.name
}

output "AZURE_CONTAINER_APPS_ENVIRONMENT_NAME" {
  description = "Name of the Container Apps environment"
  value       = module.container_app_environment.name
}

output "AZURE_CONTAINER_APPS_ENVIRONMENT_ID" {
  description = "Resource ID of the Container Apps environment"
  value       = module.container_app_environment.id
}

output "SERVICE_BACKEND_ENDPOINT_URL" {
  description = "Full URL of the backend application"
  value       = module.backend.fqdn != null ? "https://${module.backend.fqdn}" : null
}

output "SERVICE_BACKEND_NAME" {
  description = "Name of the backend container app"
  value       = module.backend.name
}

output "SERVICE_BACKEND_RESOURCE_ID" {
  description = "Resource ID of the backend container app"
  value       = module.backend.id
}

output "SERVICE_AI_SERVICE_NAME" {
  description = "Name of the AI service container app"
  value       = module.ai_service.name
}

output "SERVICE_AI_SERVICE_RESOURCE_ID" {
  description = "Resource ID of the AI service container app"
  value       = module.ai_service.id
}

output "SERVICE_WEATHER_FUNCTION_NAME" {
  description = "Name of the weather Azure Function App"
  value       = module.weather_function_app.name
}

output "SERVICE_WEATHER_FUNCTION_ENDPOINT_URL" {
  description = "Default hostname of the weather Azure Function App"
  value       = module.weather_function_app.default_hostname != null ? "https://${module.weather_function_app.default_hostname}" : null
}

output "AZURE_LOG_ANALYTICS_WORKSPACE_ID" {
  description = "ID of the Log Analytics workspace"
  value       = module.log_analytics.id
}

output "APPLICATIONINSIGHTS_CONNECTION_STRING" {
  description = "Application Insights connection string"
  value       = module.app_insights.connection_string
  sensitive   = true
}

output "AZURE_AI_FOUNDRY_PROJECT_ENDPOINT" {
  description = "Azure AI Foundry project endpoint URL"
  value       = module.ai_project.ai_foundry_project_endpoint
}

output "AZURE_AI_FOUNDRY_ENDPOINT" {
  description = "Azure AI Foundry account endpoint URL"
  value       = module.ai_foundry.ai_foundry_endpoint
}

output "AZURE_OPENAI_DEPLOYMENT_NAME" {
  description = "Name of the AI model deployment (GPT-4o)"
  value       = module.ai_foundry.ai_model_deployment_name
}

output "AZURE_CLIENT_ID" {
  description = "Client ID of the user-assigned managed identity"
  value       = module.identity.client_id
}

output "AZURE_TENANT_ID" {
  description = "Azure tenant ID"
  value       = module.identity.tenant_id
}

# Signals to azd that the backend container app already exists (provisioned by Terraform)
output "SERVICE_BACKEND_RESOURCE_EXISTS" {
  description = "Indicates backend container app is pre-provisioned"
  value       = "true"
}

# Signals to azd that the AI service container app already exists (provisioned by Terraform)
output "SERVICE_AI_SERVICE_RESOURCE_EXISTS" {
  description = "Indicates AI service container app is pre-provisioned"
  value       = "true"
}
