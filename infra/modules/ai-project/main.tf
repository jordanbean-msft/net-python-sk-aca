########## AI Foundry Project Module ##########

resource "azapi_resource" "ai_foundry_project" {
  depends_on = [
    var.ai_foundry_ready
  ]

  type                      = "Microsoft.CognitiveServices/accounts/projects@2025-06-01"
  name                      = "project${var.unique_suffix}"
  parent_id                 = var.ai_foundry_id
  location                  = var.location
  schema_validation_enabled = false
  tags                      = var.tags

  body = {
    sku = {
      name = "S0"
    }
    identity = {
      type = "SystemAssigned"
    }
    properties = {
      displayName = "project"
      description = "AI Foundry project for agents"
    }
  }

  response_export_values = [
    "identity.principalId",
    "properties.internalId"
  ]
}

resource "time_sleep" "wait_project_identities" {
  depends_on = [
    azapi_resource.ai_foundry_project
  ]
  create_duration = "30s"
}

resource "azurerm_role_assignment" "cosmosdb_operator" {
  depends_on = [
    time_sleep.wait_project_identities
  ]
  scope                = var.cosmosdb_id
  role_definition_name = "Cosmos DB Operator"
  principal_id         = azapi_resource.ai_foundry_project.output.identity.principalId
}

resource "azurerm_role_assignment" "storage_blob_contributor" {
  depends_on = [
    time_sleep.wait_project_identities
  ]
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azapi_resource.ai_foundry_project.output.identity.principalId
}

resource "azurerm_role_assignment" "search_index_contributor" {
  depends_on = [
    time_sleep.wait_project_identities
  ]
  scope                = var.ai_search_id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = azapi_resource.ai_foundry_project.output.identity.principalId
}

resource "azurerm_role_assignment" "search_service_contributor" {
  depends_on = [
    time_sleep.wait_project_identities
  ]
  scope                = var.ai_search_id
  role_definition_name = "Search Service Contributor"
  principal_id         = azapi_resource.ai_foundry_project.output.identity.principalId
}
