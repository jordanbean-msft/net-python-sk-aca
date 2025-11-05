output "id" {
  value       = azurerm_user_assigned_identity.main.id
  description = "User assigned identity resource ID"
}

output "principal_id" {
  value       = azurerm_user_assigned_identity.main.principal_id
  description = "Principal ID of the identity"
}

output "client_id" {
  value       = azurerm_user_assigned_identity.main.client_id
  description = "Client ID of the identity"
}

output "tenant_id" {
  value       = azurerm_user_assigned_identity.main.tenant_id
  description = "Tenant ID of the identity"
}
