########## Modular Root Configuration ##########

locals {
  base_tags = merge(
    var.common_tags,
    {
      environment     = "dev"
      managed_by      = "terraform",
      SecurityControl = "Ignore"
    }
  )
}

module "foundation" {
  source = "./modules/foundation"
}

locals {
  unique_suffix = var.unique_suffix != "" ? var.unique_suffix : module.foundation.unique_suffix
}


module "log_analytics" {
  source              = "./modules/log-analytics"
  create              = true
  name                = "law-${local.unique_suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  retention_in_days   = 30
  tags                = local.base_tags
}

module "app_insights" {
  source              = "./modules/app-insights"
  create              = true
  name                = "appi-${local.unique_suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = module.log_analytics.id
  application_type    = "web"
  tags                = local.base_tags
}

module "ai_foundry" {
  source                     = "./modules/ai-foundry"
  unique_suffix              = local.unique_suffix
  resource_group_name        = var.resource_group_name
  location                   = var.location
  subscription_id            = var.subscription_id
  log_analytics_workspace_id = module.log_analytics.id
  tags                       = local.base_tags
}

module "ai_project" {
  source              = "./modules/ai-project"
  unique_suffix       = local.unique_suffix
  resource_group_name = var.resource_group_name
  location            = var.location
  ai_foundry_id       = module.ai_foundry.ai_foundry_id
  ai_foundry_ready    = module.ai_foundry.ai_foundry_ready
  tags                = local.base_tags

  depends_on = [module.ai_foundry]
}

# Grant Cognitive Services OpenAI User role to managed identity on AI Foundry account
resource "azurerm_role_assignment" "managed_identity_cognitive_services_user" {
  principal_id         = module.identity.principal_id
  role_definition_name = "Cognitive Services OpenAI User"
  scope                = module.ai_foundry.ai_foundry_id
}

module "identity" {
  source              = "./modules/identity"
  name                = "uami-containerapps-${local.unique_suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = local.base_tags
}

module "acr" {
  source              = "./modules/acr"
  name                = "acr${local.unique_suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Basic"
  pull_principal_id   = module.identity.principal_id
  tags                = local.base_tags
}

module "container_app_environment" {
  source                     = "./modules/container-app-environment"
  name                       = "cae-${local.unique_suffix}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = module.log_analytics.id
  tags                       = local.base_tags
}

module "storage_account" {
  source              = "./modules/storage-account"
  name                = "st${local.unique_suffix}weather"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = local.base_tags
}

module "function_plan" {
  source              = "./modules/function-plan"
  name                = "fp-weather-${local.unique_suffix}"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = local.base_tags
  sku_size            = "EP1"
}

module "weather_function_app" {
  source                     = "./modules/function-app"
  name                       = "weather-func-${local.unique_suffix}"
  resource_group_name        = var.resource_group_name
  location                   = var.location
  storage_account_name       = module.storage_account.name
  storage_account_access_key = module.storage_account.primary_access_key
  app_service_plan_id        = module.function_plan.id
  identity_id                = module.identity.id
  tags                       = merge(local.base_tags, { azd-service-name = "weather-function" })
}

module "ai_service" {
  source                  = "./modules/container-app"
  name                    = "ca-ai-service-${local.unique_suffix}"
  environment_id          = module.container_app_environment.id
  resource_group_name     = var.resource_group_name
  image                   = coalesce(var.ai_service_image, "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest")
  cpu                     = 0.5
  memory                  = "1Gi"
  min_replicas            = 1
  max_replicas            = 10
  external_enabled        = false
  target_port             = 8000
  registry_server         = module.acr.login_server
  registry_identity_id    = module.identity.id
  identity_ids            = [module.identity.id]
  dapr_app_id             = "ai-service"
  dapr_app_port           = 8000
  dapr_log_level          = "info"
  dapr_enable_api_logging = true
  env_vars = {
    PYTHONUNBUFFERED                      = "1"
    PORT                                  = "8000"
    LOG_LEVEL                             = "info"
    AZURE_AI_PROJECT_ENDPOINT             = module.ai_foundry.ai_foundry_endpoint
    AZURE_AI_MODEL_DEPLOYMENT             = module.ai_foundry.ai_model_deployment_name
    WeatherFunctionUrl                    = "https://${module.weather_function_app.default_hostname}"
    APPLICATIONINSIGHTS_CONNECTION_STRING = module.app_insights.connection_string
    AZURE_CLIENT_ID                       = module.identity.client_id
  }
  secret_env_vars = var.azure_openai_api_key != null ? { AZURE_OPENAI_API_KEY = var.azure_openai_api_key } : {}
  tags            = merge(local.base_tags, { azd-service-name = "ai-service" })
}

module "backend" {
  source                  = "./modules/container-app"
  name                    = "ca-backend-${local.unique_suffix}"
  environment_id          = module.container_app_environment.id
  resource_group_name     = var.resource_group_name
  image                   = coalesce(var.backend_image, "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest")
  cpu                     = 0.5
  memory                  = "1Gi"
  min_replicas            = 1
  max_replicas            = 10
  external_enabled        = true
  target_port             = 8080
  registry_server         = module.acr.login_server
  registry_identity_id    = module.identity.id
  identity_ids            = [module.identity.id]
  dapr_app_id             = "backend"
  dapr_app_port           = 8080
  dapr_log_level          = "info"
  dapr_enable_api_logging = true
  env_vars = {
    PORT                       = "8080"
    ASPNETCORE_ENVIRONMENT     = "Production"
    Logging__LogLevel__Default = "Information"
    AiServiceAppId             = "ai-service"
  }
  tags = merge(local.base_tags, { azd-service-name = "backend" })
}

resource "azurerm_monitor_diagnostic_setting" "container_app_env" {
  count                      = var.enable_diagnostics ? 1 : 0
  name                       = "diag-cae-${local.unique_suffix}"
  target_resource_id         = module.container_app_environment.id
  log_analytics_workspace_id = module.log_analytics.id

  enabled_log { category = "ContainerAppConsoleLogs" }
  enabled_log { category = "ContainerAppSystemLogs" }
  enabled_metric { category = "AllMetrics" }
}
