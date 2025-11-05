########## AI Foundry Module ##########

resource "azapi_resource" "ai_foundry" {
  type                      = "Microsoft.CognitiveServices/accounts@2025-06-01"
  name                      = "aifoundry${var.unique_suffix}"
  parent_id                 = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}"
  location                  = var.location
  schema_validation_enabled = false
  tags                      = var.tags

  body = {
    kind = "AIServices"
    sku = {
      name = "S0"
    }
    identity = {
      type = "SystemAssigned"
    }
    properties = {
      disableLocalAuth       = false
      allowProjectManagement = true
      customSubDomainName    = "aifoundry${var.unique_suffix}"
      publicNetworkAccess    = "Enabled"
      networkAcls = {
        defaultAction = "Allow"
      }
    }
  }
}

resource "time_sleep" "wait_ai_foundry" {
  depends_on = [
    azapi_resource.ai_foundry
  ]
  create_duration = "30s"
}

resource "azurerm_cognitive_deployment" "gpt_4o" {
  depends_on = [
    time_sleep.wait_ai_foundry
  ]

  name                 = "gpt-4o"
  cognitive_account_id = azapi_resource.ai_foundry.id

  sku {
    name     = "GlobalStandard"
    capacity = 100
  }

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-11-20"
  }
}

resource "azurerm_monitor_diagnostic_setting" "ai_foundry" {
  count                      = var.enable_diagnostics ? 1 : 0
  name                       = "${azapi_resource.ai_foundry.name}-diag"
  target_resource_id         = azapi_resource.ai_foundry.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

