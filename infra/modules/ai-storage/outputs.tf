output "storage_account_id" {
  value = azurerm_storage_account.ai_storage.id
}

output "storage_account_name" {
  value = azurerm_storage_account.ai_storage.name
}

output "storage_account_primary_blob_endpoint" {
  value = azurerm_storage_account.ai_storage.primary_blob_endpoint
}

output "cosmosdb_id" {
  value = azurerm_cosmosdb_account.cosmosdb.id
}

output "cosmosdb_name" {
  value = azurerm_cosmosdb_account.cosmosdb.name
}

output "cosmosdb_endpoint" {
  value = azurerm_cosmosdb_account.cosmosdb.endpoint
}

output "ai_search_id" {
  value = azapi_resource.ai_search.id
}

output "ai_search_name" {
  value = azapi_resource.ai_search.name
}
