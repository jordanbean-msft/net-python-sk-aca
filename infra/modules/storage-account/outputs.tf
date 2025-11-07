output "name" { value = azurerm_storage_account.main.name }
output "primary_connection_string" { value = azurerm_storage_account.main.primary_connection_string }
output "primary_access_key" {
  value     = azurerm_storage_account.main.primary_access_key
  sensitive = true
}
