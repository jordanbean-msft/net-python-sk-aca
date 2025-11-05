########## AI Storage Module (Cosmos DB + AI Search for AI Foundry) ##########

resource "azurerm_storage_account" "ai_storage" {
  name                     = "staifoundry${var.unique_suffix}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_cosmosdb_account" "cosmosdb" {
  name                = "cosmos${var.unique_suffix}"
  resource_group_name = var.resource_group_name
  location            = var.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  tags = var.tags
}

resource "azapi_resource" "ai_search" {
  type      = "Microsoft.Search/searchServices@2024-06-01-preview"
  name      = "aisearch${var.unique_suffix}"
  parent_id = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}"
  location  = var.location
  tags      = var.tags

  body = {
    sku = {
      name = "basic"
    }
    properties = {
      replicaCount        = 1
      partitionCount      = 1
      hostingMode         = "default"
      publicNetworkAccess = "Enabled"
      semanticSearch      = "disabled"
    }
  }
}
