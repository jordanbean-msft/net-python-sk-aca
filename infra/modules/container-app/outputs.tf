output "id" {
  description = "Container App resource ID"
  value       = azurerm_container_app.main.id
}

output "name" {
  description = "Container App name"
  value       = azurerm_container_app.main.name
}

output "fqdn" {
  description = "Container App FQDN (null if no ingress)"
  value       = length(azurerm_container_app.main.ingress) > 0 ? azurerm_container_app.main.ingress[0].fqdn : null
}
